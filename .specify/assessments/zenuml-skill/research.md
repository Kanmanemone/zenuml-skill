# Idea Research: ZenUML을 그려주는 Claude Skill (품질 좋은 Context 포함)

- **Slug**: zenuml-skill
- **Created**: 2026-07-27
- **Evidence confidence (overall)**: high

## Users & Demand

- 저장소 이름 자체가 `zenuml-skill`이며, 요청자가 본인을 위해 이 skill을 만들고 싶다고 명시적으로 말함 — 요청자 개인의 dogfooding 수요. — [source: intake.md] (confidence: high, 단 표본은 1인)
- **LLM으로 시퀀스 다이어그램을 생성하는 수요 자체는 이미 관찰됨**: Atlassian 커뮤니티 포럼에서 ChatGPT로 ZenUML DSL을 생성하는 워크플로가 실제로 공유·논의되고 있고, 참여자들이 "요구사항 시각화 및 결함 발견"에 잠재 가치가 있다고 인정함. — [source: community.atlassian.com 포럼 스레드] (confidence: medium)
- 그 외 팀/조직 단위의 수요, 사용 빈도에 대한 근거는 없음 — [ASSUMPTION] (confidence: low)

## Prior Art

- **저장소 내부 선례**: 이 저장소는 이미 Spec Kit 기반 skill 15개(`.claude/skills/speckit-*`)를 보유하며, 각 skill이 지침·가드레일·템플릿을 SKILL.md에 번들링하는 패턴을 실제로 사용 중. 아이디어와 정확히 일치하는 내부 선례. — [source: repo `.claude/skills/*/SKILL.md`] (confidence: high)
- **공식 DSL 문법 레퍼런스 확보**: `mermaid-js/zenuml-core` 저장소의 `docs/DSL_SYNTAX.md`(MIT, 버전관리됨, 순수 마크다운)를 원문 기준으로 조사함. 핵심 요소: `title` 디렉티브, 참가자 선언(`@Actor`/`@Database`/`@Control`/`@SQSQueue` 등 타입 애너테이션, 색상, alias, 이모지, 최소 너비), 동기 메시지(`A.method()`, `A -> B.method(args)`, 중첩 블록), 비동기 메시지(`A -> B: text`, 반환 `A --> B: text`), 객체 생성(`new Type(args)`), `return`, 조건문(`if/else if/else`), 반복문(`while/for/loop`), `opt(condition)`, `par { }`(병렬), `critical(mutex)`, `try/catch/finally`, `section(Label)`/익명 블록, `ref(DiagramName)`(다이어그램 간 참조), `== Label ==` 구분자, `//` 주석, 유니코드/이모지, `group "Name" { }`, `@Starter(Participant)`. — [source: raw.githubusercontent.com/mermaid-js/zenuml-core/master/docs/DSL_SYNTAX.md, confirmed-by-user] (confidence: high — 원문 기반, 이전 조사보다 신뢰도 상향)
- **생태계가 최소 3갈래로 분화되어 있음**:
  1. `mermaid-js/zenuml-core` — OSS 렌더링 엔진, Mermaid 조직 산하에서 활발히 유지. Mermaid 공식 문서(`mermaid.js.org/syntax/zenuml.html`)에도 통합되어 있으나 "실험적인 lazy-loading/async 렌더링을 사용하며 향후 변경될 수 있다"고 명시. Mermaid 네이티브 `sequenceDiagram`과는 **문법이 다르다**고 공식 문서가 경고함. — [source: mermaid.js.org/syntax/zenuml.html, confirmed-by-user] (confidence: high)
  2. `ZenUml/ZenUml` — 원조 오픈소스 웹앱/이슈 트래커, 관리가 저조함(커밋 2개, PR 0개). — [source: github.com/ZenUml/ZenUml] (confidence: medium)
  3. `zenuml.com` / `app.zenuml.com` — **별도의 상업/엔터프라이즈 제품**으로 보임: "privacy-first", Amazon·ThoughtWorks·Woolworths 등 레퍼런스 고객 언급, OMG UML 2.5.1 인증, 24시간 SLA 지원을 내세움. PlantUML 대비 "2~3배 적은 줄 수"를 핵심 가치로 제시. — [source: zenuml.com, confirmed-by-user] (confidence: medium)
  - 세 갈래의 문법은 대체로 겹치지만 100% 동일하다는 보장은 없음 — 이후 `/shape` 단계에서 **어느 렌더러/배포판을 기준으로 skill을 만들지 반드시 확정**해야 함.
- **독립 리뷰(제3자)**: modeling-languages.com은 ZenUML의 강점으로 중괄호 기반 중첩 문법(PlantUML의 activate/deactivate보다 가독성이 높다), 브라우저 내 즉시 렌더링, HTML/DOM 출력(검색·커스텀 스타일 가능), "유효한 모델만 그리도록 강제"하는 구조적 제약을 꼽음. 약점으로는 시퀀스 다이어그램만 지원(클래스/패키지/배포 다이어그램 없음), 그리고 **리뷰 작성 시점 기준** 반환값/`new`/주석이 "아직 미구현"이라고 언급함 — 그러나 최신 `DSL_SYNTAX.md`에는 이 기능들이 모두 존재하므로 **이 리뷰는 시점이 오래되어 일부 내용이 이제는 사실이 아닐 가능성이 높음** (시간에 민감한 정보이므로 skill 본문에 그대로 인용하면 안 됨). — [source: modeling-languages.com, confirmed-by-user] (confidence: medium, 일부 내용 stale로 추정)
- **AI 프롬프트 메타 자료 발견**: gist(`doggy8088`)는 자연어→Mermaid/ZenUML 변환을 위한 AI 프롬프트 프레임워크로, ZenUML 섹션에 문법 요약과 함께 솔직한 한계를 명시: "ZenUML은 종종 특정 렌더러 설정(플러그인)을 필요로 하며 GitHub Markdown 같은 플랫폼에서 기본적으로 동작하지 않을 수 있다." — [source: gist.github.com/doggy8088/6b017de59eda53a018f77889ad66a38c, policy: allowlisted] (confidence: medium)

## Market & Context

- ZenUML을 쓰지 않을 경우의 대안: PlantUML(activate/deactivate 방식, 더 장황함) 또는 Mermaid 네이티브 `sequenceDiagram`(Claude 아티팩트가 네이티브 렌더링 지원). ZenUML DSL은 문법이 더 간결하다고 여러 소스가 일관되게 주장하지만, **렌더링 가능 환경이 제한적**(전용 렌더러/플러그인 필요, GitHub Markdown에서 기본 미지원)이라는 트레이드오프가 있음. — [source: modeling-languages.com, gist.github.com/doggy8088/...] (confidence: medium)
- 튜토리얼류 자료(compilatrix.com)는 문법 사용법만 다루고 "깔끔한 다이어그램 작성"에 대한 지침은 전혀 제공하지 않음 — 즉 사용자가 원하는 "질 좋은 Context"는 기존 공개 자료에 **존재하지 않는 공백**이며, 직접 만들어야 하는 부분임이 확인됨. — [source: compilatrix.com/docs/zenuml-tutorial, confirmed-by-user] (confidence: high)

## Data & Constraints

- Anthropic 공식 가이드: Claude API 실행 환경은 네트워크 접근이 없어, ZenUML 문법 레퍼런스는 skill 디렉터리에 직접 번들링해야 함. `docs/DSL_SYNTAX.md`는 MIT 라이선스의 순수 마크다운이라 `references/syntax.md`로 재구성해 넣기에 적합하다는 사용자의 판단은 라이선스·형식 면에서 타당함(재배포 시 원저작물의 MIT 라이선스 고지를 유지해야 함). — [source: platform.claude.com/docs/.../best-practices; github.com/mermaid-js/zenuml-core (LICENSE 확인은 별도 검증 필요)] (confidence: medium — LICENSE 파일 자체는 직접 확인하지 않음, `[NEEDS CLARIFICATION]`)
- 공식 가이드는 SKILL.md 본문 500줄 이하, 참조 파일은 SKILL.md에서 1단계 깊이로만 링크, 100줄 넘는 참조 파일엔 목차, "Claude가 이미 아는 내용은 넣지 말라"는 간결성 원칙을 명시. — [source: platform.claude.com/docs/.../best-practices] (confidence: high)

## Evidence Against the Idea

- **렌더링 파편화**: ZenUML 다이어그램은 전용 렌더러(zenuml-core, VS Code 확장, app.zenuml.com) 없이는 미리보기가 안 되고, GitHub Markdown 등에서 기본적으로 렌더링되지 않는다는 한계가 명확함 — 결과물을 어떻게 사용자가 검증/확인할지가 실행상 큰 리스크. — [source: gist.github.com/doggy8088/..., modeling-languages.com] (confidence: medium)
- **생태계 3분화로 인한 스펙 불확실성**: OSS 엔진(mermaid-js), 원조 웹앱(ZenUml/ZenUml), 상업 제품(zenuml.com)이 서로 다른 지향점을 가지며, 문법이 완전히 동일한지 검증되지 않음 — 잘못된 레퍼런스를 기준으로 만들면 실제 렌더러와 문법이 어긋날 위험. — [source: mermaid.js.org, github.com/ZenUml/ZenUml, zenuml.com] (confidence: medium)
- **"Context를 많이 담기"와 "간결한 결과물"의 긴장**: Anthropic 공식 skill 저작 원칙("Claude가 이미 아는 건 넣지 마라")과 사용자가 원하는 "질 좋은 Context를 함께 넣는다"는 목표는 균형이 필요 — 문서를 두껍게 만드는 것 자체가 목표가 되면 안 됨. — [source: platform.claude.com/docs/.../best-practices] (confidence: high)
- **프롬프트/Context만으로는 완전히 해결 안 될 수도 있음**: Atlassian 포럼에서 "요청받지 않은 내용을 지어내지 마라"는 프롬프트 수정을 시도했으나 결과물이 여전히 다소 장황했다고 보고됨 — 정적 스타일 가이드/Context 번들만으로는 충분치 않고, 검증 루프(생성→체크리스트 대조→수정) 같은 구조가 추가로 필요할 수 있음을 시사. — [source: community.atlassian.com 포럼] (confidence: medium)

## Supporting Evidence (문제의식 자체를 뒷받침)

- **동료 심사 학술 근거**: arXiv 논문(2404.06371)이 28개 산업 요구사항 문서에서 생성된 87개 LLM 생성 시퀀스 다이어그램을 평가함. 이해가능성·표준 준수·용어 정합성은 우수했으나, **정확성(correctness)과 완전성(completeness)이 유의미하게 낮았고**, "요약으로 인해 정보가 누락됨", "숫자·타이밍 정밀도 부족", "과도한 중첩 조건으로 다이어그램이 너무 상세해져 탐색이 어려워짐" 등의 문제가 확인됨. 논문은 **도메인 특화 지식/맥락(context)이 부족할수록 품질이 낮아진다**고 명시적으로 지적하며, 반복 정제(iterative refinement) 메커니즘의 필요성을 제안함. — [source: arxiv.org/html/2404.06371v2, confirmed-by-user] (confidence: high)
- 이는 사용자의 핵심 가설(맹목적인 텍스트→다이어그램 변환은 부족하고, 질 좋은 Context가 결합돼야 깔끔한 결과가 나온다)을 직접적으로 뒷받침하는 가장 강한 근거임.

## Gaps & Open Questions

- [NEEDS CLARIFICATION: 어느 ZenUML 생태계/렌더러를 최종 타겟으로 하는가 — `mermaid-js/zenuml-core`(Mermaid 계열, OSS) vs `zenuml.com`(상업 제품) vs VS Code 확장? 이번 조사에서 OSS 엔진 쪽이 유지보수가 활발하고 문법 문서가 버전관리되어 가장 좋은 재료로 보이지만, 최종 결정은 `/shape` 단계에서.]
- [NEEDS CLARIFICATION: 결과물을 어떻게 렌더링/미리보기할 것인가 — 렌더링 불가 환경(GitHub Markdown 등)에서는 순수 텍스트 DSL만 제공하고 사람이 별도 도구로 확인하는 흐름을 전제할 것인가?]
- [NEEDS CLARIFICATION: `references/syntax.md`로 재구성 시 원문 MIT 라이선스 고지를 어떤 형태로 유지할 것인가 — LICENSE 파일 자체는 아직 확인하지 않음.]
- [NEEDS CLARIFICATION: "깔끔함"을 정적 스타일 가이드만으로 담보할지, 아니면 (Atlassian 포럼 사례가 시사하듯) 생성→검증 체크리스트 대조 같은 피드백 루프까지 skill 워크플로에 포함할지?]

## Sources

- https://github.com/mermaid-js/zenuml-core (host: github.com, policy: allowlisted)
- https://github.com/ZenUml/ZenUml (host: github.com, policy: allowlisted)
- https://raw.githubusercontent.com/mermaid-js/zenuml-core/master/docs/DSL_SYNTAX.md (host: raw.githubusercontent.com, policy: confirmed-by-user)
- https://mermaid.js.org/syntax/zenuml.html (host: mermaid.js.org, policy: confirmed-by-user)
- https://zenuml.com (host: zenuml.com, policy: confirmed-by-user)
- https://zenuml.com/blog/zenuml-makes-sequence-diagrams-easier-and-faster/ (host: zenuml.com, policy: confirmed-by-user)
- https://app.zenuml.com/help.html (host: app.zenuml.com, policy: confirmed-by-user)
- https://gist.github.com/doggy8088/6b017de59eda53a018f77889ad66a38c (host: gist.github.com, policy: allowlisted)
- https://modeling-languages.com/zenuml-drawing-sequence-diagram-easier-faster/ (host: modeling-languages.com, policy: confirmed-by-user)
- https://www.compilatrix.com/docs/zenuml-tutorial (host: compilatrix.com, policy: confirmed-by-user)
- https://community.atlassian.com/forums/App-Central-discussions/A-brand-new-way-to-create-sequence-diagrams-with-ChatGPT/td-p/2344110 (host: community.atlassian.com, policy: confirmed-by-user)
- https://arxiv.org/html/2404.06371v2 (host: arxiv.org, policy: confirmed-by-user)
- https://docs.zenuml.com/sequence-diagram-syntax.html (host: docs.zenuml.com, policy: confirmed-by-user — 이전 조사 시 페이지 내용이 placeholder/TODO였음, 이번 raw DSL_SYNTAX.md 원문으로 대체·상회됨)
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (host: platform.claude.com, policy: confirmed-by-user — 원 요청 docs.claude.com에서 리다이렉트)
