# Problem Definition: 질 좋은 Context로 깔끔한 ZenUML 다이어그램을 생성하는 문제

- **Slug**: zenuml-skill
- **Created**: 2026-07-27
- **Inputs used**: intake.md, research.md

## Problem Statement

Claude에게 자연어 설명만으로 ZenUML 시퀀스 다이어그램을 그려달라고 요청하면, 문법 오류는 없더라도 요청받지 않은 내용을 지어내거나("fluff"), 불필요하게 장황하고 군더더기 많은 결과물이 나오기 쉽다 — 이는 도메인 특화 맥락(정확한 DSL 문법, 어떤 렌더러를 쓰는지, "깔끔함"의 기준) 없이 매번 즉흥적으로 생성하기 때문이다. 현재 이 저장소에는 이런 맥락을 한 곳에 묶어 재사용 가능하게 만드는 수단이 없어, 매번 사용자가 직접 스타일을 설명하고 결과물을 수동으로 다듬어야 한다.

## Affected Users & Stakeholders

- **Users**: 저장소 소유자(요청자) 본인 — Claude Code로 ZenUML 다이어그램을 생성/문서화할 때 이 문제를 직접 겪음. — [source: intake.md]
- **Stakeholders**: 저장소 소유자 — skill의 범위·품질 기준을 결정. 그 외 이 skill로 만든 다이어그램을 읽게 될 잠재적 독자(팀원, 문서 소비자)가 있는지는 불명확. — [NEEDS CLARIFICATION: 이 skill의 결과물을 저장소 소유자 본인 외에 다른 사람도 소비하는가? (개인용 vs 공유/배포용)]

## Goals

- Claude가 입력에 **명시적으로 존재하는 참가자/메시지/흐름만** 반영하고, 요청되지 않은 내용을 지어내지 않는다 — Atlassian 포럼에서 관찰된 "fluff" 문제를 직접 겨냥. (research.md, Supporting Evidence)
- 생성된 DSL이 **문법적으로 정확**하고, 목표 렌더러에서 오류 없이 렌더링된다.
- ZenUML DSL 문법·스타일 규칙이 **skill 디렉터리 안에 번들링**되어 있어, 네트워크 접근 없이도(Claude API 실행 환경 제약) 매번 일관된 품질을 낸다. (research.md, Data & Constraints)
- 결과물이 "깔끔하고 군더더기 없다"는 것을 사람이 판단할 수 있는 구체적 기준(안티패턴 목록, 체크리스트 등)을 갖춘다.

## Non-Goals

- 새로운 UML 렌더러나 다이어그램 뷰어를 직접 구현하지 않는다 — 기존 ZenUML 렌더러(어느 쪽이든, 확정은 shape 단계) 생태계를 그대로 사용한다.
- 시퀀스 다이어그램 이외의 UML 다이어그램 타입(클래스, 배포 등)은 다루지 않는다 — ZenUML 자체가 시퀀스 다이어그램 전용이므로. (research.md, Prior Art)
- 여러 사람이 동시에 쓰는 팀 배포/거버넌스(공유 스타일 가이드 합의, 조직 전체 표준화)는 이번 범위에 포함하지 않는다 — 대상 사용자가 아직 개인으로 한정됨.
- 렌더링 미리보기 환경 자체를 구축하는 것(예: GitHub Markdown에서 안 보이는 문제의 근본 해결)은 범위 밖 — 어떤 렌더러를 전제할지는 열린 질문으로 남긴다.

## Success Metrics

- **정확성(품질, 정성적)**: 생성된 다이어그램을 원본 설명과 대조했을 때, 명시되지 않은 참가자·메시지·분기가 추가되지 않는다 (baseline: 없음 — 현재는 skill 없이 매번 즉흥 생성, 비교 기준 자체가 없음).
- **문법 정확성**: 생성된 DSL이 목표 렌더러에서 파싱/렌더링 오류 없이 표시된다 (baseline: 알 수 없음 — 렌더러 미확정 상태이므로 측정 불가, `[NEEDS CLARIFICATION]`).
- **재사용성(정성적)**: 매번 스타일을 처음부터 설명하지 않아도, skill이 로드된 상태에서 일관된 결과가 나온다 (baseline: 현재는 매번 재설명 필요 — 이 자체가 문제의식의 근거).

## Cost of Inaction

이 skill을 만들지 않으면, 사용자는 ZenUML 다이어그램이 필요할 때마다 Claude에게 문법과 스타일 기준을 매번 새로 설명해야 하고, 그럼에도 research.md에서 확인된 것처럼(Atlassian 포럼 사례, arXiv 논문 2404.06371) 프롬프트만으로는 "지어낸 내용"과 "과도한 상세함" 문제가 완전히 해결되지 않아 결과물을 수동으로 재검토·수정하는 비용이 반복적으로 발생한다. 규모가 개인 사용 수준이라 당장 큰 비용은 아니지만, 반복 작업의 누적 비효율이 baseline이다.

## Open Questions

- [NEEDS CLARIFICATION: 이 skill의 결과물을 저장소 소유자 본인 외에 다른 사람도 소비하는가? (개인용 vs 공유/배포용)]
- [NEEDS CLARIFICATION: 어느 ZenUML 생태계/렌더러를 최종 타겟으로 하는가 — `mermaid-js/zenuml-core`(OSS) vs `zenuml.com`(상업 제품) vs VS Code 확장? (research.md, Gaps)]
- [NEEDS CLARIFICATION: 결과물을 어떻게 렌더링/미리보기할 것인가 — 렌더링 불가 환경(GitHub Markdown 등)에서는 순수 텍스트 DSL만 제공하고 사람이 별도 도구로 확인하는 흐름을 전제할 것인가? (research.md, Gaps)]
- [NEEDS CLARIFICATION: `references/syntax.md`로 재구성 시 원문(mermaid-js/zenuml-core, MIT) 라이선스 고지를 어떤 형태로 유지할 것인가? (research.md, Gaps)]
- [NEEDS CLARIFICATION: "깔끔함"을 정적 스타일 가이드만으로 담보할지, 생성→검증 체크리스트 대조 같은 피드백 루프까지 skill 워크플로에 포함할지? (research.md, Gaps)]
- [NEEDS CLARIFICATION: 입력 소스 범위 — 자연어 설명만 지원하는가, 기존 코드베이스 분석이나 다른 다이어그램 형식(Mermaid/PlantUML) 변환도 지원하는가? (intake.md)]
