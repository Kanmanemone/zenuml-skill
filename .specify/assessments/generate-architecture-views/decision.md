# Decision: 자연어 설명에서 구조 뷰(컴포넌트/그룹/의존성)를 생성하는 신규 스킬

- **Slug**: generate-architecture-views
- **Decided**: 2026-07-31
- **Verdict**: go
- **Artifacts reviewed**: intake.md, research.md, problem.md, concept.md

## Scorecard

| Criterion | Rating | Justification |
|-----------|--------|---------------|
| Problem validity | adequate | `generating-zenuml-diagrams`의 SKILL.md가 "코드베이스 분석"과 "비-시퀀스 다이어그램"을 명시적으로 out-of-scope로 선언하고 있어 구조 정보 공백이 문서상으로도 확인됨(problem.md). 다만 수요는 요청자 본인 1인의 dogfooding에 그침 — 표본이 작아 `strong`은 아님. |
| Evidence strength | adequate | 프로그램 이해 학계 이론(Pennington, von Mayrhauser & Vans)과 실증 연구(CodeMap, arXiv 2504.04553), 실무 관행(C4/ADR)이 "구조가 행동보다 먼저 필요하다"는 방향성을 반복적으로 뒷받침함. 단, 사용자가 제시한 정확한 "5단계 파이프라인"은 단일 학술 이론으로 검증되지 않음(research.md Claim Check에서 명시)을 정직하게 반영해 `strong`이 아닌 `adequate`로 낮춤. |
| Value vs. inaction | adequate | 아무것도 안 하면 사용자는 계속 수작업(코드 직접 읽기)에 의존하거나 입력 모델이 다른 외부 도구(`swark`)로 이탈해야 함(problem.md Cost of Inaction). 반면 해결 비용은 concept.md에서 `small` 로 산정되어 가치가 비용을 상회. |
| Feasibility / appetite | strong | concept.md Option A는 기존 스킬이 이미 검증한 파일 배치·렌더링 경로·anti-fluff 정신을 그대로 재사용하는 `small` 규모 옵션이며, 스코프 블로우업 지점(자동 그룹핑 정교화)도 명시적으로 식별·제한됨. |
| Strategic fit | strong | 이 저장소의 존재 목적 자체가 "질 좋은 Context를 갖춘 다이어그램 생성"이며(`.specify/assessments/zenuml-skill/research.md`), 시퀀스 다이어그램만으로는 부족한 구조적 맥락을 보강하는 이 아이디어는 저장소의 근본 목표와 직접 정렬됨. |
| Risk posture | adequate | 주요 리스크(그룹핑 신호 부족 시 그룹이 하나로 퇴화, VS Code에서의 `subgraph` 렌더링 미재검증, 두 스킬 분리로 인한 발견성 저하)가 concept.md "Assumptions to Validate"에 명시적으로 식별되고 좁은 스코프로 완화 경로도 제시됨 — 다만 아직 검증되지 않은 가정으로 남아 있어 `strong`은 아님. |

## Verdict & Rationale

**go.** Problem validity와 Evidence strength가 모두 `adequate` 이상이며(가드레일 기준 충족), concept.md가 리스크를 명확히 이해하고 좁은 스코프(Option A, small appetite)로 완화한 추천안을 제시했다. 표본이 1인이라는 근본적 약점과 "5단계 이론"이 검증된 정설이 아니라는 점을 research.md가 이미 정직하게 인정했음에도, (1) 문제 자체가 저장소의 기존 문서(SKILL.md의 명시적 out-of-scope 선언)로 독립 검증되고, (2) 방향성을 뒷받침하는 여러 독립 증거가 존재하며, (3) 해결 비용이 `small`로 매우 낮아 리스크 대비 기대 가치가 충분하다고 판단해 `needs-clarification`이 아닌 `go`로 판정한다. 단, 아래 열린 질문들은 결정을 뒤집을 정도는 아니지만 명세 단계에서 반드시 좁혀야 한다.

## If go — Handoff to `/speckit-specify`

- **Problem**: `generating-zenuml-diagrams`는 행동(Behavior)만 다루어, 사용자가 컴포넌트·그룹·의존관계 같은 구조적 mental model을 별도 수작업 없이 얻을 수 없다.
- **Chosen approach**: concept.md Option A — 자연어 프로세스 설명을 입력으로 받는 **별도의 새 스킬**. 참가자(Components)를 자동 그룹핑(Grouping)한 `subgraph`와 의존관계(Dependencies)를 화살표로 표현한 Mermaid `graph`/`flowchart` 한 장을 생성하고, 설계 의도(Intent)는 별도 섹션이 아닌 `%%` 인라인 주석으로 필요한 곳에만 간결하게 붙인다. 산출물은 기존 `.zenuml/<slug>.md`와 슬러그를 공유하는 형제 파일에 저장한다.
- **In scope**: 자연어 설명 기반 구조 그래프 생성 / 자동 그룹핑(설명에 명시된 단서만 사용) / 인라인 Intent 주석 / 기존 `.zenuml/` 파일 배치·렌더링 관례 재사용.
- **Out of scope**: 실제 코드베이스 정적 분석 / 클래스·배포 등 임의 UML 유형 지원 / 근거 없는 Intent 추측 / 다이어그램 지속 자동 동기화 / 기존 `generating-zenuml-diagrams`의 SKILL.md 수정 / 결합도 분석 등 정교한 그룹핑 알고리즘.
- **Success metrics**: (정성적) 산출물만 보고 사용자가 별도 코드 탐색 없이 컴포넌트·그룹·의존관계를 설명할 수 있다 / 기존 `.zenuml/<slug>.md` 워크플로에 자연스럽게 얹혀 별도 도구·절차 학습이 필요 없다.
- **Carried-forward open questions** (명세 단계 또는 `/speckit-clarify`에서 좁혀야 함):
  - [NEEDS CLARIFICATION: 새 스킬 산출물의 정확한 파일 경로/이름 규칙 — problem.md는 `.zenuml/<slug>.structure.md` 류의 형제 파일을 참고안으로 제시했으나 최종 확정은 아님]
  - [NEEDS CLARIFICATION: "자동 그룹핑"이 실제로 참조할 신호(네임스페이스, 설명 내 계층 언급 등)의 구체적 규칙]
  - [NEEDS CLARIFICATION: Intent 주석을 "모든 요소"에 달지 "모호함이 예상되는 요소"에만 선별적으로 달지, 후자라면 그 판단 기준]
  - [NEEDS CLARIFICATION: 두 스킬(시퀀스/구조) 간 상호 발견성 — 이번 범위에서는 배제했으나, 실사용 중 필요성이 드러나면 후속 반복에서 재검토]
  - [NEEDS CLARIFICATION (검증 필요, 결정을 뒤집진 않음): Mermaid `subgraph` + `%%` 주석 조합이 VS Code 내장 Markdown Mermaid 프리뷰에서 문제없이 렌더링되는지 실제 확인 필요]
