# Problem Definition: 다이어그램별 개선 이력 로깅 + 후속 Spec Kit 개선 파이프라인

- **Slug**: diagram-feedback-log
- **Created**: 2026-07-28
- **Inputs used**: intake.md, research.md

## Problem Statement

`generating-zenuml-diagrams` skill이 생성한 다이어그램이 사용자 기대에 못 미칠 때, 현재는 채팅 안에서 즉석으로 개선점을 말하고 재생성을 요청하는 것 외에 다른 경로가 없다. 이 교정 과정(무엇이 부족했는지, 어떻게 고쳤는지)은 대화가 끝나는 순간 그대로 휘발되어, 같은 종류의 부족함이 다음 요청에서도 반복되고 다이어그램을 다듬을 때마다 매번 "주먹구구식 후속 질문"이 되풀이된다. 이는 사용자가 스스로 밝힌 1원칙("Zen UML을 한 번 만들고 나서 주먹구구식 후속 질문으로 계속 다듬는 상황을 만들지 말자")을 정면으로 위반하는 상태이며, feature 001의 자체 decision.md가 이미 남긴 "정적 체크리스트만으로 충분한가"라는 질문에 답할 실사용 데이터도 전혀 쌓이지 않는다.

## Affected Users & Stakeholders

- **Users**: 저장소 소유자 본인(요청자) — `generating-zenuml-diagrams` skill을 직접 사용하며 다이어그램을 재생성 요청할 때마다 이 문제를 겪는다. — [source: intake.md, research.md Users & Demand] (표본 1인, confidence: high)
- **Stakeholders**: 저장소 소유자 본인이 사용자이자 유일한 의사결정자·시간 투자자를 겸한다. 이 로그를 재료로 삼을 미래의 Spec Kit 실행(즉, "다음에 이 저장소를 개선하려는 미래의 나")도 사실상의 이해관계자다. — [ASSUMPTION]
- 이 메커니즘이 `generating-zenuml-diagrams` 외 다른 스킬에도 재사용되는 일반 패턴인지는 미확정이므로, 그 경우의 잠재 이해관계자(미래 스킬 유지보수자)는 [NEEDS CLARIFICATION: 이 저장소의 다른 미래 스킬에도 재사용 가능한 일반 패턴으로 설계해야 하는지 — research.md Gaps에서 이월]

## Goals

- 다이어그램 하나에 대한 교정 사이클(최초 요청 + 최초 결과 + 개선점 + 재생성 결과, 필요시 여러 라운드까지 체인으로) 전체를 대화 종료 후에도 남는 형태로 보존한다.
- 그렇게 보존된 이력을 나중에 "지금 무엇을 개선해야 하는가"를 판단할 때 선택적으로 참조할 수 있는 재료로 만든다 — 전량을 매번 쓰는 것이 아니라, feature별로 관련 있는 항목만 추려 쓴다.
- 실제로 무언가를 고칠 때는 임의 수정이 아니라 Spec Kit 파이프라인을 통과시켜, 로그에서 발견한 패턴이 검증된 절차를 거쳐 반영되게 한다.
- 1원칙("한 번 만들고 나서 주먹구구식 후속 질문으로 계속 다듬는 상황을 만들지 않는다")이 매 다이어그램마다 반복 위반되는 상태를 끝낸다 — 정확히는, 위반이 일어나더라도 그 위반의 흔적이 다음 개선에 쓰일 수 있게 만든다.

## Non-Goals

- 다이어그램 품질을 높이는 구체적 방법론(예: 특정 체크리스트 항목 추가) 자체를 이 단계에서 확정하지 않는다 — 이 아이디어는 "방법론을 만드는 방법론"이며 개별 개선안이 아니다. — [source: intake.md, Restated]
- 로그를 분석해 패턴을 자동으로 제안하는 요약/분석 도구는 이번 범위에 포함하지 않는다(포함 여부 자체가 미결) — [NEEDS CLARIFICATION: "패턴이 보인다"는 판단이 전적으로 수동인지, 로그 요약/분석 기능도 이번 범위인지 — research.md Gaps에서 이월]
- 팀/조직 단위 거버넌스나 다인 사용자 협업은 다루지 않는다 — 확인된 사용자는 1인뿐이다. — [source: research.md, Users & Demand]
- 기존의 정적 자기검증 루프(AP-1~AP-5, 생성 직후 제시 전 수행)를 대체하지 않는다 — 이 문제는 "제시 이후, 사용자가 만족하지 못했을 때"부터 시작되는 별개의 국면을 다룬다. — [source: .claude/skills/generating-zenuml-diagrams/SKILL.md, research.md Prior Art]
- `generating-zenuml-diagrams` 외 스킬로의 일반화는 이번 정의 단계에서 전제하지 않는다 — 적용 범위는 미결로 남긴다. — [NEEDS CLARIFICATION: 이월, 위 Affected Users 참고]

## Success Metrics

- 사용자가 AskUserQuestion의 "[개선점 전달 및 재생성]"을 선택한 모든 사이클에 대해, 예외 없이 로그 항목 하나가 생성/누적된다 (완결성, 정성적 — 코드 검사로 확인 가능). (baseline: 0 — 현재 이런 로그가 전혀 존재하지 않음)
- "[아무것도 안 함]"을 선택한 경우에는 로그에 아무것도 추가되지 않는다 (over-logging 방지, 정성적). (baseline: 해당 분기 자체가 존재하지 않음)
- 로그 항목이 실제로 특정 미래 Spec Kit 실행(예: `/speckit-specify`)의 근거 자료로 인용된 사례가 최소 1건 이상 발생한다 — 이것이 이 메커니즘이 "죽은 인프라"가 아니라는 것을 입증하는 궁극적 지표다 (정성적, 장기 지표). (baseline: 0, 아직 메커니즘 자체가 없음)
- [NEEDS CLARIFICATION: 위 지표들을 측정할 최소 관찰 기간이나 다이어그램 재생성 발생 빈도에 대한 실측 근거가 없음 — research.md Gaps에서 이월]

## Cost of Inaction

아무것도 만들지 않으면, 다이어그램 재생성 때마다 겪는 교정 과정은 지금처럼 채팅 안에서만 존재하다 대화가 끝나면 사라지는 상태가 계속된다. 같은 종류의 부족함이 다음 요청에서도 형태만 바꿔 반복될 가능성이 높고, 사용자가 스스로 세운 1원칙은 매번 새로 위반된다. 또한 feature 001의 decision.md가 이미 명시적으로 남긴 "정적 체크리스트+자기검증 루프만으로 충분한가"라는 질문은, 실사용에서 무엇이 부족했는지를 보여줄 데이터가 하나도 쌓이지 않으므로 영영 근거를 갖고 답할 수 없는 채로 남는다. 반대로, research.md의 "Evidence Against the Idea"가 지적하듯 무대응의 비용 자체가 아주 크지는 않다 — 지금도 채팅으로 즉석 재생성은 가능하며, 단지 그 이력이 누적되지 않을 뿐이다.

## Open Questions

- [NEEDS CLARIFICATION: AskUserQuestion 확인 단계는 다이어그램이 성공적으로 생성된 모든 경우에 항상 붙는가, 아니면 특정 조건에서만 붙는가?] (intake.md → research.md에서 이월)
- [NEEDS CLARIFICATION: "개선점 전달"의 구체적 UX 흐름(자유 텍스트 입력 단계 등)은?] (intake.md → research.md에서 이월)
- [NEEDS CLARIFICATION: 로깅 디렉토리의 정확한 위치/이름과 버전관리 여부 — research.md는 `.specify/` 계열처럼 버전관리 대상으로 두는 쪽이 기존 관례와 일관된다고 유추했으나 확정은 아니다.]
- [NEEDS CLARIFICATION: 로그 아이템의 파일 포맷/스키마는?] (intake.md → research.md에서 이월)
- [NEEDS CLARIFICATION: 이 메커니즘이 `generating-zenuml-diagrams` 하나에만 적용되는지, 저장소 내 다른 미래 스킬에도 재사용 가능한 일반 패턴으로 설계해야 하는지?] (intake.md → research.md에서 이월)
- [NEEDS CLARIFICATION: "패턴이 보인다"는 판단이 전적으로 수동인지, 로그 요약/분석 기능도 이번 범위인지?] (intake.md → research.md에서 이월)
- [NEEDS CLARIFICATION: 로그 아이템이 feature 재료로 소비된 뒤에도 남아있는지, 소비됨으로 표시/보관되는지?] (intake.md → research.md에서 이월)
- [NEEDS CLARIFICATION: 로깅·재생성 루프 자체가 "패턴이 쌓일 만큼" 충분히 자주 발생할지에 대한 실측 근거가 없다 — 성공 지표의 관찰 기간과 직결된다.] (research.md에서 이월)
