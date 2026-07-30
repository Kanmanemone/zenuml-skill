# Decision: 다이어그램별 개선 이력 로깅 + 후속 Spec Kit 개선 파이프라인

- **Slug**: diagram-feedback-log
- **Decided**: 2026-07-28
- **Verdict**: go
- **Artifacts reviewed**: intake.md, research.md, problem.md, concept.md

## Scorecard

| Criterion | Rating | Justification |
|-----------|--------|---------------|
| Problem validity | strong | 1원칙 위반이라는 사용자 진술에 더해, 재조사에서 실제 재생성 사유 두 범주(참가자 구분 기준 이견, 겉핥기식 다이어그램)와 "일일이 입력 못할 만큼" 잦았다는 요청자 직접 진술이 확보됐다 — 막연한 원칙 선언이 아니라 구체적이고 반복적인 실패 유형으로 뒷받침된다 — research.md, Users & Demand |
| Evidence strength | adequate | research.md 자체 신뢰도가 low-medium에서 medium으로 상향됐다. 이전 결정의 두 blocking question(재생성 빈도, 패턴 판단 신뢰도)에 대해 유일한 이해관계자의 직접 진술이 추가됐다. 다만 여전히 정량 데이터가 아닌 사후 회상 기반 정성적 진술이고 제3자가 원문을 대조할 수 없어 `strong`까지는 아니다 — research.md |
| Value vs. inaction | adequate | 문제가 실재하고 반복된다는 근거는 강화됐지만, problem.md의 Cost of Inaction 자체는 "무대응 비용이 아주 크지는 않다"는 서술을 그대로 유지하고 있어 시급성 자체를 `strong`으로 올릴 근거는 아직 없다 — problem.md |
| Feasibility / appetite | adequate | concept.md Option A는 small 규모를 유지했고, 이번 세션에서 두 차례 반복 검증(2단계 UX 제거, AskUserQuestion 기술적 불가능성 확인 후 평범한 채팅 질문으로 대체)을 통과해 구체성이 높아졌다 — concept.md |
| Strategic fit | unknown | `.specify/memory/constitution.md`가 여전히 미채움 템플릿이라 대조할 공식 원칙이 없다 — feature 001의 decision.md와 동일한 제약이며, 그 결정에서도 이 상태로 go가 내려진 선례가 있다 — .specify/memory/constitution.md, .specify/assessments/zenuml-skill/decision.md |
| Risk posture | strong | 이전에 미완화 상태였던 두 핵심 리스크(재생성 빈도 미검증, 패턴 판단 신뢰도 미검증)가 이번 재조사에서 유일한 이해관계자의 직접 진술로 해소됐다. shape 단계에서도 실제로 구현 불가능했던 UX 설계를 스키마 검증으로 걸러냈다. 남은 리스크(정확한 로그 스키마, 스킵 신호 판정 규칙, 언급 감지 트리거 구현)는 모두 specify 단계에서 다룰 수 있는 설계 디테일 수준이지 존재를 위협하는 리스크가 아니다 — concept.md, research.md |

## Verdict & Rationale

**go.** Problem validity가 `strong`, evidence strength가 `adequate`(never weak/unknown 기준 충족)이며, concept.md가 구체적인 추천 옵션(Option A)을 제시했으므로 go 기준을 충족한다. 직전 `needs-clarification` 판정을 내렸던 결정적 이유는 evidence strength가 `weak`였기 때문인데, 그 근거였던 두 blocking question — "재생성이 실제로 자주 발생하는가"와 "사람이 로그에서 패턴을 안정적으로 판단할 수 있는가" — 이 이번 재조사에서 요청자 본인의 직접 진술로 답변됐다. 정량적 실측치가 아니라는 한계는 명시적으로 남기지만(Evidence strength, adequate — strong은 아님), 이 저장소처럼 사용자가 1인뿐인 도구에서는 그 1인의 직접 진술이 확보 가능한 최선의 증거이며, 그것으로 evidence strength를 weak에서 adequate로 끌어올리기에 충분하다고 판단한다. Strategic fit이 `unknown`인 점은 feature 001 때와 동일하게 감추지 않고 명시하되, 그 결정에서도 blocking 사유로 취급하지 않은 선례를 그대로 따른다.

## If go — Handoff to `/speckit-specify`

- **Problem**: `generating-zenuml-diagrams`가 생성한 다이어그램이 기대에 못 미칠 때 채팅 안에서 즉석으로만 교정이 이뤄지고 그 이력이 휘발되어, 같은 유형의 부족함(참가자 구분 기준 이견, 겉핥기식 다이어그램 등)이 반복되고 사용자의 1원칙("한 번 만들고 나서 주먹구구식 후속 질문으로 계속 다듬지 않는다")이 매번 위반된다.
- **Chosen approach**: concept.md Option A — 최소 로깅(AskUserQuestion 재활용 + 선별적 스테이징). 다이어그램 제시 직후 AskUserQuestion을 다시 사용하되, 질문 문구 자체에 hint를 담고("고치고 싶은 점이 있다면 적어주세요 — 없으면 아래에서 골라주세요"), 라벨 옵션은 [아무것도 안 함]과 [사유 없이 다시 생성] 두 개로 채운다. 구체적 개선점은 도구가 자동 제공하는 자유 텍스트("Other")에 바로 입력한다 — 별도 후속 질문 없이 한 번의 상호작용으로 끝난다. "아무것도 안 함"을 고르면 짧고 고정된 응답만 오가 토큰 소비가 사실상 0에 가깝다. 사이클(최초 요청·최초 결과·개선점·재생성 결과)은 다이어그램 하나당 파일 하나에 이어붙인다. 로그 디렉토리는 기본적으로 `.zenuml/`처럼 gitignore 대상이며, 어떤 Spec Kit 실행이 특정 항목을 실제로 인용하는 순간에만 그 파일 하나를 `git add`로 지연 스테이징한다.
- **In scope**: `generating-zenuml-diagrams` 스킬 하나에 한정된 최소 로깅 메커니즘. 다이어그램별 교정 사이클 보존, 스킵 시 무기록, 인용 시점 선별적 버전관리 편입.
- **Out of scope**: 로그 요약/분석 자동화나 패턴 자동 탐지, `generating-zenuml-diagrams` 외 스킬로의 일반화·공유 인터페이스, 팀/조직 단위 협업·거버넌스, 기존 정적 자기검증 루프(AP-1~AP-5)의 대체, 로그 항목의 "소비됨" 상태 자동 추적 — concept.md, Out of Scope
- **Success metrics**: (1) "개선점 전달" 응답이 있었던 모든 사이클에 대해 예외 없이 로그 항목이 생성/누적됨(완결성). (2) 스킵 신호일 때는 로그에 아무것도 추가되지 않음. (3) 최소 1건 이상의 미래 Spec Kit 실행이 특정 로그 항목을 실제로 인용함 — 이 메커니즘이 죽은 인프라가 아님을 입증하는 장기 지표. 모두 baseline 0(현재 메커니즘 자체가 없음) — problem.md, Success Metrics
- **Carried-forward open questions**:
  - [NEEDS CLARIFICATION: 정확한 로그 디렉토리 이름/경로]
  - [NEEDS CLARIFICATION: 로그 아이템의 파일 포맷/스키마 및 라운드가 이어질 때의 갱신 방식(append 세부 형식)]
  - [NEEDS CLARIFICATION: 두 번째 필수 라벨("사유 없이 다시 생성")의 정확한 문구와, 그것이 선택됐을 때(개선점 텍스트 없이 재생성만 요청된 경우) 로그에 무엇을 기록할지 — concept.md, Option A Rabbit holes. ~~채팅 질문의 스킵 신호 판정 모호성~~은 AskUserQuestion 구조화 선택지로 회귀하면서 해소됨.]
  - [NEEDS CLARIFICATION: "언급/인용"을 감지해 `git add`를 트리거하는 구체적 메커니즘 — 에이전트의 실제 인용 행위에 결부시키는 결정론적 방식으로 구현해야 토큰 비용 위험을 피할 수 있다는 원칙은 concept.md에 명시되어 있으나, 정확한 구현은 미정 — concept.md, "토큰 소비 우려에 대한 개념 수준 점검"]
  - [NEEDS CLARIFICATION: 로그 아이템이 feature 재료로 소비된 뒤에도 계속 남아있는지, 소비됨으로 표시/보관되는지]
  - [정보용, 비차단: 재생성 요청의 정확한 빈도(예: 생성 10회 중 몇 회)는 여전히 정량화되지 않았다 — 정성적 신호로 go 판정에는 충분하다고 보았으나, specify 단계의 우선순위 판단에는 참고만 할 것]
