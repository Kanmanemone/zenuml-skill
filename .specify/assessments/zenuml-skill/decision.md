# Decision: 질 좋은 Context로 깔끔한 ZenUML 다이어그램을 생성하는 Skill

- **Slug**: zenuml-skill
- **Decided**: 2026-07-27
- **Verdict**: go
- **Artifacts reviewed**: intake.md, research.md, problem.md, concept.md

## Scorecard

| Criterion | Rating | Justification |
|-----------|--------|---------------|
| Problem validity | adequate | 문제 자체는 명확하고 구체적(맥락 없는 생성 → fluff/부정확)이지만, 확인된 사용자는 요청자 1인뿐 — problem.md, Affected Users |
| Evidence strength | strong | 원문 DSL 레퍼런스(MIT, 버전관리)를 직접 확보했고, 동일 문제(LLM이 지어낸 내용을 추가함)를 보고하는 실제 포럼 사례와, 이를 뒷받침하는 동료심사 학술 논문(arXiv 2404.06371)까지 확보 — research.md, Supporting Evidence |
| Value vs. inaction | adequate | 방치 시 비용은 크지 않지만 반복적으로 발생하고, 이미 좋은 재료가 확보돼 있어 지금 만들 이유가 분명함 — problem.md, Cost of Inaction |
| Feasibility / appetite | strong | Option B는 small~medium 범위이고, 저장소에 이미 15개 skill을 이 패턴으로 만든 내부 선례가 있어 실행 가능성이 높음 — concept.md, Option B |
| Strategic fit | unknown | 이 저장소의 `.specify/memory/constitution.md`가 아직 템플릿 placeholder 상태([PROJECT_NAME] 등 미채움)라 대조할 공식 프로젝트 원칙이 없음 — 상충되는 원칙은 없지만 확인 자체가 불가능함을 그대로 인정함 |
| Risk posture | adequate | 렌더러 3분화, 라이선스 고지, "체크리스트만으로 fluff가 실제로 줄어드는가" 같은 리스크가 있으나 Option B가 이를 명시적으로 좁혀 완화하고, 평가 시나리오로 검증하는 계획까지 포함 — concept.md, Rabbit holes / Assumptions to Validate |

## Verdict & Rationale

**go.** Problem validity가 adequate 이상이고, evidence strength가 strong으로 `weak`/`unknown`이 아니며, concept.md에서 구체적인 추천 옵션(Option B)이 나왔으므로 go 기준을 충족한다. 특히 evidence strength가 이 아이디어를 밀어붙이는 결정적 근거다 — 단순한 열의가 아니라, 동일 문제를 겪는 실제 사례(Atlassian 포럼)와 이를 설명하는 학술적 근거(arXiv 논문: 컨텍스트 부족이 LLM 다이어그램 품질 저하의 원인)가 사용자의 가설을 직접 뒷받침한다. Strategic fit이 `unknown`인 점은 감추지 않고 명시한다 — 이 저장소의 constitution이 아직 채워지지 않아 공식적으로 대조할 원칙이 없을 뿐, 상충되는 신호는 발견되지 않았다. Value vs. inaction과 Problem validity가 `adequate`(strong이 아님)인 이유는 확인된 사용자가 1인뿐이라는 점 때문이며, 이는 handoff에서 열린 질문으로 명확히 이어간다.

## If go — Handoff to `/speckit-specify`

- **Problem**: 맥락(정확한 DSL 문법·스타일 기준) 없이 자연어만으로 ZenUML 시퀀스 다이어그램을 생성하면, 요청받지 않은 내용이 추가되거나 불필요하게 장황한 결과가 나온다.
- **Chosen approach**: concept.md Option B — `mermaid-js/zenuml-core`의 `docs/DSL_SYNTAX.md`(MIT)를 재구성한 문법 레퍼런스와, "입력에 없는 내용을 지어내지 않는다"는 명시적 규칙 + 흔한 안티패턴 체크리스트를 SKILL.md/참조 파일로 번들링하고, 생성 후 "원본 대조 → 체크리스트 검증 → 필요시 수정"하는 자기검증 루프를 워크플로에 포함한다. 렌더러는 `mermaid-js/zenuml-core` 기준 DSL을 1차 타겟으로 확정한다.
- **In scope**: 자연어 설명 → 정확하고 군더더기 없는 ZenUML DSL 텍스트 생성. 문법 레퍼런스 및 스타일 체크리스트 번들링.
- **Out of scope**: 새 렌더러/뷰어 구현, 시퀀스 외 다이어그램 타입, 팀 단위 배포·거버넌스, 렌더링 미리보기 환경 자체 구축, 자연어 외 입력(코드베이스 분석·타 형식 변환), `zenuml.com` 상업 제품/VS Code 확장과의 공식 호환성 보장.
- **Success metrics**: (1) 생성된 다이어그램이 원본 설명에 없는 참가자/메시지/분기를 포함하지 않음(정성적 대조), (2) 생성된 DSL이 목표 렌더러(`mermaid-js/zenuml-core`)에서 오류 없이 렌더링됨, (3) skill 로드 상태에서 매번 스타일을 재설명하지 않아도 일관된 결과가 나옴(정성적).
- **Carried-forward open questions**:
  - [NEEDS CLARIFICATION: 이 skill의 결과물을 저장소 소유자 본인 외에 다른 사람도 소비하는가? (개인용 vs 공유/배포용)]
  - [NEEDS CLARIFICATION: `mermaid-js/zenuml-core` 기준 DSL 문법이 사용자가 실제로 확인할 렌더러/뷰어 환경과 호환되는지 — 사용자가 어떤 도구로 결과물을 미리 볼 것인지 확정 필요]
  - [NEEDS CLARIFICATION: `docs/DSL_SYNTAX.md`(MIT) 재구성 시 라이선스 고지를 어떤 형태·위치로 유지할 것인가]
  - [NEEDS CLARIFICATION: 정적 체크리스트 + 자기검증 루프만으로 충분한지, 아니면 추가 검증 도구/스크립트가 필요한지는 실사용 테스트로 확인 필요]
