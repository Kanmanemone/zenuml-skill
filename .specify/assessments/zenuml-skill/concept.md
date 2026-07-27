# Concept: 질 좋은 Context로 깔끔한 ZenUML 다이어그램을 생성하는 Skill

- **Slug**: zenuml-skill
- **Created**: 2026-07-27
- **Recommended option**: Option B — Reference + Anti-Fluff 체크리스트 + 자기검증 루프

## Options

### Option A — 순수 레퍼런스 번들 (가장 작은 버전)
- **Sketch**: SKILL.md에 최소 지침만 두고, `mermaid-js/zenuml-core`의 `docs/DSL_SYNTAX.md`를 재구성한 `references/syntax.md` 하나만 번들링한다. Claude는 이 참조 파일을 읽고 문법적으로 정확한 ZenUML DSL 텍스트를 생성한다. 스타일/안티패턴 규칙이나 검증 단계는 없음 — "정확한 문법으로 생성"까지만 보장한다.
- **Appetite**: small (하루 이내)
- **Trade-offs**: 가장 빠르게 만들 수 있고 유지보수 부담이 최소화된다. 하지만 problem.md의 핵심 목표인 "요청되지 않은 내용을 지어내지 않는다"는 부분은 전혀 담보하지 못한다 — research.md의 Atlassian 포럼 사례가 보여주듯, 문법 레퍼런스만으로는 "fluff" 문제가 해결되지 않는다. 사실상 문제의 절반(문법 정확성)만 푼다.
- **Rabbit holes**: 없음(범위가 작아서) — 오히려 "너무 적게 만들어서 원래 문제를 안 푼다"는 반대 방향 리스크가 있다.

### Option B — 레퍼런스 + Anti-Fluff 체크리스트 + 자기검증 루프
- **Sketch**: Option A의 문법 레퍼런스에 더해, (1) "입력에 명시되지 않은 참가자·메시지·분기를 추가하지 않는다"는 명시적 규칙과 흔한 안티패턴 목록(과도한 중첩, 불필요한 try/catch, 근거 없는 반환값 등)을 담은 스타일 가이드를 번들링하고, (2) 생성 후 "원본 설명과 대조 — 체크리스트 통과 여부 확인 — 필요시 수정"하는 워크플로를 SKILL.md에 명시한다(Anthropic 공식 가이드의 "generate → validate → fix" 피드백 루프 패턴, research.md 참고). 렌더러는 `mermaid-js/zenuml-core` 기준 DSL을 1차 타겟으로 확정하고, SKILL.md에 그렇게 명시한다.
- **Appetite**: medium (며칠 정도 — 참조 파일 재구성, 체크리스트 작성, 3개 이상 평가 시나리오로 테스트)
- **Trade-offs**: problem.md의 핵심 목표(정확성 + 군더더기 없음 + 재사용 가능한 일관성)를 직접 겨냥한다. Option A보다 SKILL.md/참조 파일을 더 신중하게 다듬어야 하고, "체크리스트가 실제로 fluff를 걸러내는가"는 실사용 테스트로 검증해야 한다(공식 가이드가 강조하는 "평가 먼저 만들기" 원칙과 부합). 렌더러 3분화 문제는 "OSS 엔진 기준"으로 명시적으로 좁혀 리스크를 줄이지만, 상업 제품(zenuml.com)이나 다른 렌더러와 100% 호환된다는 보장은 없다.
- **Rabbit holes**: (1) 체크리스트를 과도하게 정교하게 만들려다 SKILL.md가 비대해질 위험(공식 가이드의 "간결함" 원칙과 충돌) — 체크리스트는 짧게 유지하고 상세 규칙은 별도 참조 파일로 분리해야 한다. (2) "깔끔함"의 기준 자체가 주관적이라 체크리스트 항목을 계속 늘리고 싶은 유혹이 있다 — 처음엔 problem.md에서 확인된 핵심 문제(지어낸 내용, 과도한 상세함)만 다루고 확장은 실사용 피드백 이후로 미뤄야 한다.

### Option C — 다중 렌더러/다중 입력 지원 풀 플랫폼
- **Sketch**: Option B에 더해, 실제 렌더링/미리보기 스크립트(zenuml-core 또는 CLI 도구 연동), 도메인별 예시 라이브러리(인증 플로우, API 호출, 에러 처리 등 템플릿), 그리고 자연어 외 입력(기존 코드베이스 분석, Mermaid/PlantUML 다이어그램 변환)까지 지원한다.
- **Appetite**: large (수 주 이상)
- **Trade-offs**: 가장 완결된 경험을 제공할 수 있지만, problem.md의 non-goals("새 렌더러 미구현", "렌더링 미리보기 환경 구축은 범위 밖", "팀 단위 거버넌스 제외")를 정면으로 위반한다. 현재 확인된 수요는 요청자 1인뿐이라(research.md, Users & Demand) 이 정도 투자를 정당화할 근거가 부족하다.
- **Rabbit holes**: Node/npm 기반 렌더러를 Windows 환경에 통합하는 작업, 여러 입력 형식 파서 유지보수, 예시 라이브러리를 "질 좋게" 유지하는 지속적 노력 — 전형적인 스코프 무한 확장 패턴이다.

## Recommendation

**Option B**를 권장한다. problem.md의 목표는 정확성뿐 아니라 "지어내지 않음"과 "군더더기 없음"을 명시적으로 요구하는데, Option A는 이를 전혀 다루지 않고 Option C는 problem.md가 이미 범위 밖으로 명시한 것들(새 렌더러, 미리보기 환경, 다중 입력)을 끌어들인다. Option B는 research.md에서 확인된 가장 강한 두 근거 — Atlassian 포럼의 "프롬프트만으로는 fluff가 안 없어진다"는 관찰과, arXiv 논문의 "도메인 컨텍스트 부족이 품질 저하의 원인"이라는 결론 — 을 정확히 겨냥하며, Anthropic 공식 skill 저작 가이드의 권장 패턴(참조 파일 번들링 + 검증 피드백 루프)과도 부합한다. 현재 확인된 수요 규모(개인 1인)에 견줘 적절한 appetite이기도 하다.

"아무것도 만들지 않는다" 옵션은 명시적으로 기각한다 — problem.md의 Cost of Inaction에 따르면 비용이 크지는 않지만 반복적으로 발생하며, 이미 구체적 해결 재료(원문 DSL 레퍼런스, 구체적 안티패턴 사례)가 확보되어 있어 지금 만들지 않을 이유가 약하다.

## Out of Scope (for the recommended option)

- 새로운 렌더러/뷰어 구현 (problem.md 상속)
- 시퀀스 다이어그램 외 UML 타입 (problem.md 상속)
- 팀/조직 단위 배포·거버넌스 (problem.md 상속)
- 렌더링 미리보기 환경 자체 구축 (problem.md 상속)
- 자연어 설명 외 입력(코드베이스 분석, 타 다이어그램 형식 변환) — Option C로 미룸
- `zenuml.com` 상업 제품이나 VS Code 확장과의 호환성 공식 보장 — 1차 타겟은 OSS 엔진(`mermaid-js/zenuml-core`) 문법 하나로 한정

## Assumptions to Validate

- `mermaid-js/zenuml-core` 기준 DSL 문법이 사용자가 실제로 다이어그램을 확인할 렌더러(예: 사용자의 에디터/뷰어 환경)와 호환된다. (problem.md Open Question과 직결 — 아직 확정되지 않음)
- 정적 체크리스트 + 자기검증 루프만으로 "fluff" 문제가 실사용에서 충분히 줄어든다 — 검증되지 않으면 추가 피드백 루프 강화가 필요할 수 있다(research.md, Atlassian 포럼 사례가 이 리스크를 시사).
- `docs/DSL_SYNTAX.md`(MIT)를 재구성해 `references/syntax.md`에 넣을 때, 적절한 라이선스 고지만으로 재배포 요건을 충족한다.
- 이 skill의 소비자는 당분간 저장소 소유자 본인으로 한정된다 — 이 가정이 깨지면(팀 공유가 필요해지면) Option B의 범위를 재검토해야 한다.
