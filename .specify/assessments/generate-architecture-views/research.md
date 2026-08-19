# Idea Research: 구조 이해를 위한 아키텍처 뷰 생성 스킬

- **Slug**: generate-architecture-views
- **Created**: 2026-07-31
- **Evidence confidence (overall)**: medium

## Claim Check: "Mental Model은 5단계로 형성된다" (사용자 제시: Components → Grouping → Dependencies → Behavior → Intent)

**결론: 부분적으로만 사실. 이 정확한 5단계 파이프라인을 명시한 단일 학술 이론은 발견되지 않았다. 그러나 "구조를 먼저, 행동을 그다음에, 의도/근거를 별도 층위로" 이해한다는 방향성 자체는 여러 독립적 출처에서 반복적으로 뒷받침된다.**

- 프로그램 이해(program comprehension) 학계의 대표 이론들(Letovsky 1986, Pennington 1987, von Mayrhauser & Vans 1994/1995, Brooks 1983, Soloway & Ehrlich)을 조사한 결과, 이 중 정확히 "Components → Grouping → Dependencies → Behavior → Intent" 5단계로 명명된 이론은 없음. 대신:
  - **Pennington(1987)**은 두 가지 표상을 구분: (1) 프로그램 모델(텍스트 기반, 마이크로구조→매크로구조로 상향식 조립 — 대략 Components/Dependencies/Behavior에 해당), (2) 상황 모델(situation model, 프로그램의 목표와 그 목표를 달성하는 기능적 수단 — 대략 Intent에 해당). — [source: researchgate.net/publication/4206083, cs.kent.edu/~jmaletic 강의자료] (confidence: high, cited)
  - **von Mayrhauser & Vans의 통합 메타모델**은 상향식(Pennington 계열)·하향식(Soloway/Ehrlich, 목표 중심)·지식기반(Letovsky)을 하나로 결합 — 역시 "구조 먼저, 목표/의도 별도"라는 이분법과 부합하지만 5단계 선형 파이프라인은 아님. — [source: cs.kent.edu/~jmaretic/.../von_mayrhauser95.pdf] (confidence: high, cited)
  - **최근 실증 연구**("Understanding Codebase like a Professional", arXiv 2504.04553, 2025)는 코드 감사자(auditor)가 실제로 **3단계 계층적 이해 흐름**을 따른다고 보고: Global(프로젝트 개요·아키텍처·구조적 관계) → Local(모듈·핵심 파일·컴포넌트 상호작용) → Detailed(구체적 코드·실행 경로). 참가자들은 "high-level information"을 먼저 보고, "주요 컴포넌트와 그 관계, 핵심 파일"을 파악한 뒤에야 함수 구현으로 들어갔다고 보고됨. 이는 사용자 주장의 "Components/Grouping/Dependencies가 Behavior보다 선행해야 한다"는 핵심과 방향이 일치. — [source: arxiv.org/html/2504.04553v2, confirmed-by-user] (confidence: high, cited)
  - 같은 논문은 정적 시각화 도구(Understand 등)만으로는 부족하다는 간접 증거도 제공: 참가자들이 인터페이스를 "복잡하고 어수선하다"고 느껴 결국 코드를 직접 읽는 방식으로 돌아갔고, 기존 도구는 "구조적 관계를 표현하고 계층적 추론 흐름을 지원하는 메커니즘이 부족하다"고 저자들이 명시. — [source: 동일 논문] (confidence: medium, cited — 이 도구 자체는 시퀀스 다이어그램 도구가 아니라 정적 분석 도구를 비판한 것이므로, "시퀀스 다이어그램이 부족하다"는 사용자 주장에 대한 직접 증거는 아니고 유비 증거임)
  - **C4 모델**(Simon Brown)은 Context → Container → Component → Code의 4단계 확대(zoom) 모델로 구조를 층위별로 나누지만, 이는 "추상화 레벨"의 분해이지 "mental model이 형성되는 인지적 순서"에 대한 이론이 아님 — 목적이 다름. — [source: c4model.com] (confidence: high, cited)
- **평가**: 사용자가 제시한 5단계는 기존 프로그램 이해 이론들의 핵심 통찰(구조가 행동보다 먼저 필요하다, 의도/근거는 별도의 상위 층위다)을 실용적으로 재구성한 **타당한 휴리스틱**으로 보이나, 하나의 검증된 인용 가능한 이론이 아니라 **사용자 자신의 종합(synthesis)**일 가능성이 높다. `research.md`나 향후 스킬 문서에 "학계에서 확립된 5단계 이론"이라고 인용하면 근거 없는 주장이 되므로, "여러 프로그램 이해 이론에서 공통적으로 뒷받침되는 실용적 프레임워크" 정도로 표현하는 것을 권장.
- [NEEDS CLARIFICATION: 사용자가 이 5단계를 어디서 접했는지(자체 고안 / 특정 아티클·강의 인용) — 특정 출처가 있다면 재확인 필요]

## Practical Operationalization: 5단계를 실무적으로 어떻게 파악할 것인가

**결론: 5단계를 새로운 다이어그램 체계로 발명하지 말고, 각 단계를 이미 업계에서 검증된 가벼운(lightweight) 기존 산출물에 1:1로 대응시키는 것이 가장 실용적이고 효과적이다.** 여러 독립 출처가 "4+1로 사고를 구조화하고, C4로 그림을 그리고, arc42/ADR로 트레이드오프·근거를 설명하라"는 조합형 실무 권장안에 수렴한다. — [source: linkedin.com/pulse/effective-architecture-documentation-arc42-c4-torsten-mosis, crashedmind.github.io/PlantUMLHitchhikersGuide/C4] (confidence: medium — 실무 블로그/가이드 수준, 동료심사 학술 소스는 아님)

이 저장소 맥락에 맞춰 5단계 각각을 대응시키면:

| 단계 | 무엇을 답하는가 | 실무에서 이미 검증된 가벼운 산출물 | 이 저장소와의 관계 |
|---|---|---|---|
| 1. Components | 무엇이 존재하는가? | C4 **Component/Container 다이어그램** — "정적 구조를 상향식 줌 레벨로 나눈다"는 목적에 특화, 학습곡선이 낮은 것으로 반복 인용됨 | 신규: 참가자 목록을 나열하는 간단한 산출물로 충분, 별도 다이어그램 불필요할 수 있음 |
| 2. Grouping | 어떻게 묶이는가? | C4 Container 레벨의 클러스터링, 또는 Mermaid **subgraph**로 표현 | 사용자가 제안한 "subgraph 포함 mermaid" 아이디어와 정확히 일치 |
| 3. Dependencies | 누가 누구를 의존하는가? | Mermaid **의존성 그래프(`graph`/`flowchart` + 화살표)**, C4의 relationship 표기 | 사용자가 제안한 핵심 산출물 |
| 4. Behavior | 실제로 어떻게 동작하는가? | **시퀀스 다이어그램** (arc42의 Runtime View, C4 Dynamic 다이어그램과 동일 역할) | **이미 `generating-zenuml-diagrams`가 충족** — 새로 만들 필요 없음 |
| 5. Intent | 왜 이렇게 설계했는가? | **ADR(Architecture Decision Record)** — "결정 하나당 한 페이지, context/options/consequences" 형식의 짧은 산문. 다이어그램이 아니라 텍스트라는 점이 핵심 | 신규: 다이어그램으로는 원천적으로 표현 불가능한 영역이므로, 별도의 짧은 "왜" 섹션(자유 서술)으로만 실용적으로 채울 수 있음 |

— [source: adr.github.io, cognitect.com/blog/2011/11/15/documenting-architecture-decisions] (confidence: high — ADR은 업계에서 10년 이상 검증된, "가장 leverage 높은 문서화 관행 중 하나"로 반복 인용됨)

**추가로 확인된 실무 패턴**: 숙련된 엔지니어들이 실제로 새 코드베이스를 파악할 때 쓰는 방법은 이론적 프레임워크를 순서대로 따르기보다 "넓게 본 뒤 좁혀가는 다중 패스(multi-pass)" 방식 — 먼저 큰 그림(다이어그램/문서/팀원 설명)을 보고, 그다음 아키텍처·데이터 흐름으로 좁히고, 마지막에 구현 세부로 들어감. 이는 이번 조사에서 이미 확인한 CodeMap 논문의 Global→Local→Detailed 3단계와도 일치하며, "5단계를 각각 독립된 산출물로 만들되 열람 순서는 위 표의 1→5 순서를 권장 진입점으로만 제시"하는 것이 실용적이라는 근거가 됨(강제 순서가 아니라 권장 진입점). — [source: dev.to/lessonsfromproduction/the-mental-model-i-use-before-touching-any-codebase-10bj, ahmadwkhan.medium.com] (confidence: medium — 실무자 블로그, 정량적 검증 없음)

**실용성 관점에서 가장 중요한 시사점**: 이번 아이디어(의존성 그래프 추가)는 5단계 중 **1~3단계(Components/Grouping/Dependencies)를 그림 하나로 동시에 충족**시킬 수 있는 효율적 지점이다 — Mermaid `graph`에 subgraph로 그룹을 묶고 화살표로 의존성을 표시하면 자연스럽게 "무엇이 있는가 + 어떻게 묶이는가 + 누가 누굴 의존하는가"가 한 산출물에 담긴다. 4단계는 이미 해결됨. 5단계(Intent)만 다이어그램이 아닌 별도의 짧은 텍스트 산출물로 처리해야 한다는 것이 구조적으로 명확해짐 — 이는 `/speckit-assess-define`에서 스코프를 좁히는 데 바로 쓸 수 있는 실무적 결론.

## Users & Demand

- 요청자 본인이 기존 `generating-zenuml-diagrams` 스킬 사용 중 "시퀀스 다이어그램만으로는 구조를 알 수 없다"는 한계를 직접 겪고 제기함 — 1인 dogfooding 수요. — [source: intake.md] (confidence: high, 표본 1인)
- **시장에서 유사 수요가 이미 관찰됨**: `swark-io/swark`(VS Code 확장, LLM으로 코드에서 Mermaid 아키텍처 다이어그램 자동 생성)가 정확히 "코드만 봐서는 아키텍처를 파악하기 어렵다"는 동일한 문제의식으로 만들어진 실제 오픈소스 도구. 온보딩 시 의존성 그림이 없으면 신규 합류자가 큰 그림을 못 본다는 문제의식이 명시적으로 언급됨. — [source: github.com/swark-io/swark, mermaidcreator.com 검색 스니펫] (confidence: medium)

## Prior Art

- **내부 선례 — 현재 스킬의 명시적 범위 제한**: `generating-zenuml-diagrams/SKILL.md`(158행)는 "Non-sequence diagrams (class, deployment, component, etc.): ZenUML supports sequence diagrams only"와 "Converting an existing Mermaid/PlantUML diagram, or analyzing a codebase to produce a diagram: out of scope for this skill"를 **명시적 Out-of-scope로 선언**하고 있음. 즉 사용자가 원하는 "의존성 그래프 추가"는 현재 스킬 문서가 스스로 배제한 영역과 정면으로 부딪힌다 — 확장이 아니라 스코프 재정의가 필요함을 시사. — [source: .claude/skills/generating-zenuml-diagrams/SKILL.md:156-158] (confidence: high)
- **내부 선례 — 입력 방식**: 현재 스킬의 입력은 "자연어로 서술된 프로세스"뿐이며 코드베이스 분석은 지원하지 않음(위와 동일 근거). 사용자가 원하는 의존성 그래프의 "누가 누구를 의존하는가"는, 실제 코드베이스를 분석하지 않고도 **자연어 설명에 이미 담긴 참가자/호출 관계**(현재 시퀀스 다이어그램이 이미 그리는 것과 동일한 정보)에서 파생 가능할 수 있음 — 즉 반드시 코드 분석 기능을 새로 만들어야 하는 것은 아닐 수 있음. [ASSUMPTION — 이 저장소가 실제로 어떤 입력(자연어 설명 vs 실제 코드)을 기준으로 할지는 intake.md의 미해결 질문] (confidence: low)
- **외부 선례 1 — `swark-io/swark`**: GitHub Copilot(LLM)을 이용해 소스코드에서 Mermaid.js 다이어그램을 자동 생성하는 VS Code 확장. 동작 방식: (1) 폴더에서 코드 파일 수집 → (2) 프롬프트 구성 → (3) LLM 호출 → (4) Mermaid 코드가 담긴 마크다운 파일로 결과 표시. Mermaid 다이어그램에서 순환(cycle)이 생기면 렌더링 실패를 막기 위해 자동 수정하는 기능도 있음(이는 의존성 그래프에서 순환 의존성이 실제로 자주 발생하는 문제라는 방증). 이 도구는 **실제 소스코드**를 입력으로 받는다는 점이 현재 저장소 스킬(자연어 입력)과 근본적으로 다름. — [source: github.com/swark-io/swark, confirmed-by-user] (confidence: high)
- **외부 선례 2 — Mermaid subgraph를 이용한 의존성 그래프**: Mermaid의 `subgraph ... end` 구문으로 서비스/모듈을 팀·계층·도메인별로 클러스터링해 표현하는 것이 일반적인 관행으로 검색됨(예: 티어별 서비스 그룹핑). 사용자가 요청한 "subgraph가 명시된 mermaid 의존성 그래프"는 이미 업계에서 통용되는 패턴과 일치. — [source: WebSearch 스니펫 — 원문 mermaidcreator.com/blog/mermaid-dependency-graph-visualization 페이지는 404로 직접 확인 실패, 검색엔진 스니펫만 확보] (confidence: low — 원문 미확인, 스니펫 기반)
- **선행 조사(zenuml-skill 원 assessment)와의 연결**: `.specify/assessments/zenuml-skill/research.md`가 이미 인용한 arXiv 논문(2404.06371)은 LLM이 생성한 시퀀스 다이어그램이 "정확성·완전성이 낮고, 도메인 맥락이 부족할수록 품질이 떨어진다"고 지적한 바 있음. 이번 조사에서 확인한 CodeMap 논문(2504.04553)의 "정적 도구만으로는 계층적 추론 흐름을 지원 못 한다"는 지적과 결을 같이함 — **컨텍스트 보강용 보조 산출물(의존성 그래프)을 추가한다는 이번 아이디어의 방향은 두 개의 독립된 선행 조사 결과와 일관됨.** — [source: .specify/assessments/zenuml-skill/research.md] (confidence: medium)

## Market & Context

- 코드/설계를 이해하지 못한 채 시퀀스 다이어그램만 보고 작업할 경우의 대안(현재 상태): 사용자가 직접 코드를 읽거나, 별도 도구(IDE의 "Find Usages", 정적 분석기, C4 다이어그램을 수작업으로 그리기)를 사용 — 모두 수동이고 시퀀스 다이어그램 워크플로와 분리되어 있어 매끄럽지 않음. — [ASSUMPTION, 이 저장소 사용 맥락 한정] (confidence: low)
- "아키텍처 다이어그램을 LLM으로 자동 생성"이라는 카테고리 자체는 이미 여러 도구(swark, 그 외 검색에서 발견된 llmermaid 등)가 존재하는 성숙 중인 시장 — 완전히 새로운 개념은 아니며, 차별점은 "이 저장소의 기존 ZenUML 시퀀스 다이어그램 워크플로와 얼마나 매끄럽게 통합되는가"에 있을 가능성이 큼. — [source: WebSearch 스니펫(github.com/fladdict/llmermaid 등)] (confidence: low, 스니펫만 확인)

## Data & Constraints

- 현재 스킬은 순수 텍스트(ZenUML DSL, Mermaid `zenuml` 코드 블록)만 파일로 출력하며 이미지 렌더링은 하지 않음(SKILL.md:159). 새 의존성 그래프 산출물도 동일하게 Mermaid `graph`/`flowchart` 텍스트로 `.zenuml/<slug>.md` 계열 파일에 추가하는 형태가 기존 아키텍처와 정합적일 것으로 보임. — [source: .claude/skills/generating-zenuml-diagrams/SKILL.md] (confidence: high)
- Mermaid `graph`/`flowchart`의 `subgraph` 문법 자체는 VS Code 내장 Markdown Mermaid 프리뷰에서 표준으로 지원되므로(zenuml과 달리 실험적 확장이 아님), 현재 스킬이 이미 확인한 "VS Code Markdown Preview Mermaid Support" 렌더링 경로를 그대로 재사용할 수 있을 가능성이 높음. [ASSUMPTION — 이번 조사에서 VS Code Mermaid 확장의 subgraph 지원 여부를 별도로 재검증하지는 않음, 다만 subgraph는 Mermaid 표준 flowchart 문법의 오래된 핵심 기능이라 위험도는 낮다고 판단] (confidence: medium)

## Evidence Against the Idea

- **스코프 충돌**: 현재 스킬 문서가 "코드베이스 분석"과 "비-시퀀스 다이어그램"을 명시적으로 out-of-scope로 선언하고 있어(SKILL.md:156-158), 이 아이디어를 기존 스킬의 "확장"으로 처리하면 스킬 자신의 문서화된 경계와 모순됨 — `/speckit-assess-shape` 단계에서 "완전히 새 스킬" vs "기존 스킬의 명시적 스코프 변경"을 결정해야 함.
- **중복 도구 존재 리스크**: `swark`처럼 "코드 → Mermaid 아키텍처 다이어그램" 문제를 이미 다루는 도구가 있음. 다만 swark는 실제 소스코드 분석 기반이고 이 저장소 스킬은 자연어 설명 기반이라는 점에서 입력 방식이 다르므로 직접 경쟁이라기보다는 인접 카테고리 — 그러나 "바퀴를 다시 만드는 것은 아닌지" 자체 점검이 필요.
- **"5단계 이론"을 그대로 근거로 내세우는 것의 리스크**: 위 Claim Check에서 확인했듯 이 5단계는 단일 검증된 학술 이론이 아니라 사용자의 종합에 가까움. 스킬 설계 문서에 "이것이 mental model 형성의 정설이다"라고 단정적으로 쓰면 사실과 다른 근거를 제시하는 셈이 되므로, 설계 근거를 "실용적 휴리스틱, 여러 이론에서 방향성만 뒷받침됨"으로 톤다운해야 함.
- **의존성 그래프 하나로 5단계 전부를 못 채움**: 사용자 스스로도 "지금은 (4) Behavior만 충족한다"고 진단했지만, 의존성 그래프를 추가해도 커버되는 것은 (1) Components, (3) Dependencies 정도이며 (2) Grouping은 subgraph로 부분 커버, (5) Intent(왜 이렇게 설계했는가)는 다이어그램만으로는 여전히 충족되지 않음 — 도식 산출물만으로 5단계 전체를 만족시키기는 구조적으로 어려움. `/speckit-assess-define` 단계에서 "이번 스킬이 5단계 중 정확히 어디까지를 목표로 하는가"를 명확히 좁혀야 함.

## Gaps & Open Questions

- [NEEDS CLARIFICATION: 이 스킬의 입력이 실제 코드베이스인가, 아니면 기존과 동일하게 자연어 프로세스 설명인가? swark류 도구처럼 코드베이스를 분석한다면 완전히 새로운 입력 파이프라인이 필요하고, 자연어 설명에서 파생한다면 기존 스킬의 확장에 가깝다.]
- [NEEDS CLARIFICATION: "Grouping"(2단계)을 무엇을 기준으로 나눌 것인가 — 사용자가 직접 그룹을 지정하는가, 자연어 설명에서 자동 추론하는가?]
- [NEEDS CLARIFICATION: "Intent"(5단계, 왜 이렇게 설계했는가)는 다이어그램으로 표현 불가능한 정보인데, 이 스킬 범위에 포함할 것인가 아니면 명시적으로 제외할 것인가?]
- [NEEDS CLARIFICATION: 사용자가 제시한 5단계의 출처 — 직접 고안한 것인지 특정 자료를 인용한 것인지]
- [NEEDS CLARIFICATION: 결과물 파일 구조 — 기존 `.zenuml/<slug>.md` 안에 의존성 그래프를 같이 넣을지, 별도 파일(`.zenuml/<slug>-deps.md` 등)로 분리할지]

## Sources

- https://www.linkedin.com/pulse/effective-architecture-documentation-arc42-c4-torsten-mosis (host: linkedin.com, policy: auto-refused — WebSearch 스니펫만 사용)
- https://crashedmind.github.io/PlantUMLHitchhikersGuide/C4/c4.html (host: crashedmind.github.io, policy: auto-refused — WebSearch 스니펫만 사용)
- https://adr.github.io/ (host: adr.github.io, policy: auto-refused — WebSearch 스니펫만 사용)
- https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions (host: cognitect.com, policy: auto-refused — WebSearch 스니펫만 사용)
- https://dev.to/lessonsfromproduction/the-mental-model-i-use-before-touching-any-codebase-10bj (host: dev.to, policy: auto-refused — WebSearch 스니펫만 사용)
- https://ahmadwkhan.medium.com/a-senior-engineers-guide-to-mastering-new-codebases-quickly-070446a1383c (host: medium.com, policy: auto-refused — WebSearch 스니펫만 사용)
- https://www.cs.kent.edu/~jmaletic/cs63903/Lecture-%20Prog%20Under.pdf (host: cs.kent.edu, policy: auto-refused — WebSearch 스니펫만 사용, 직접 fetch 안 함)
- https://www.researchgate.net/publication/4206083_A_cognitive_model_for_program_comprehension (host: researchgate.net, policy: auto-refused — WebSearch 스니펫만 사용)
- https://www.cs.kent.edu/~jmaletic/cs69995-PC/papers/von_mayrhauser95.pdf (host: cs.kent.edu, policy: auto-refused — WebSearch 스니펫만 사용)
- https://arxiv.org/html/2504.04553v2 (host: arxiv.org, policy: confirmed-by-user)
- https://c4model.com/ (host: c4model.com, policy: auto-refused — WebSearch 스니펫만 사용)
- https://github.com/swark-io/swark (host: github.com, policy: allowlisted)
- https://www.mermaidcreator.com/blog/mermaid-dependency-graph-visualization (host: mermaidcreator.com, policy: confirmed-by-user — fetch 시도했으나 404, 검색 스니펫만 확보)
- https://github.com/fladdict/llmermaid (host: github.com, policy: allowlisted — 존재만 확인, 상세 미조사)
- .claude/skills/generating-zenuml-diagrams/SKILL.md (내부 저장소 파일)
- .specify/assessments/zenuml-skill/research.md (내부 저장소 파일)
