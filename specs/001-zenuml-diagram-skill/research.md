# Phase 0 Research: ZenUML Diagram Skill

이 문서는 `plan.md`의 Technical Context에 남아 있던 구현 수준 결정 사항을 정리한다. 문제/증거/컨셉 수준 조사는 이미 `.specify/assessments/zenuml-skill/research.md`에서 완료되었으므로, 여기서는 그 결론을 계승해 **skill을 실제로 어떻게 구성할지**에 대한 남은 결정만 다룬다.

## Decision: Skill 이름

- **Decision**: `generating-zenuml-diagrams`
- **Rationale**: Anthropic 공식 skill 저작 가이드는 gerund(동명사) 형태(`processing-pdfs`, `analyzing-spreadsheets`)를 명명 규칙으로 권장한다. `zenuml`, `diagram`, `generating` 키워드를 포함해 discovery(description 매칭)에 유리하고, 소문자·숫자·하이픈만 사용하며 예약어(`claude`, `anthropic`)를 포함하지 않아 규칙을 만족한다.
- **Alternatives considered**: `zenuml-skill`(이 저장소/평가 슬러그와 동일해 혼동 가능, 너무 포괄적), `zenuml-diagrams`(명사구, 허용되지만 gerund보다 discovery 신호가 약함), `clean-zenuml-generator`("clean"이 마케팅 용어처럼 읽혀 description 매칭에 불리).

## Decision: 참조 파일 구조

- **Decision**: `SKILL.md` 하나 + `references/syntax.md` 하나. `SKILL.md`에서 `references/syntax.md`로 정확히 1단계 깊이로만 링크한다.
- **Rationale**: Anthropic 가이드의 "참조 파일은 SKILL.md에서 1단계 깊이로만" 규칙과, `docs/DSL_SYNTAX.md` 원문이 100줄을 넘는 분량이므로 목차를 상단에 두라는 권장을 그대로 따른다. 이번 스킬은 도메인이 하나(ZenUML DSL)뿐이므로 `reference/finance.md` 식의 도메인별 분리 패턴은 불필요하다.
- **Alternatives considered**: 모든 내용을 SKILL.md 본문에 인라인(간단하지만 500줄 제한에 근접·초과할 위험, 매 세션 컨텍스트 비용 증가); 참조 파일을 문법/스타일 두 개로 분리(과설계 — 이번 범위에선 하나로 충분).

## Decision: 안티패턴 체크리스트 항목

- **Decision**: 자기검증 체크리스트는 다음 항목으로 시작한다 — (1) 설명에 없는 참가자가 추가되지 않았는가, (2) 설명에 없는 메서드 호출/메시지가 추가되지 않았는가, (3) 설명에 없는 조건 분기·반복이 추가되지 않았는가, (4) 근거 없는 `try/catch`나 반환값이 삽입되지 않았는가, (5) 동일 로직을 표현할 수 있는 가장 얕은 중첩 구조를 사용했는가.
- **Rationale**: (1)~(4)는 `.specify/assessments/zenuml-skill/research.md`의 Atlassian 포럼 사례("ChatGPT가 시나리오에 없는 fluff를 추가")와 arXiv 논문(2404.06371)의 "Too Detailed"/완전성 문제를 직접 겨냥한다. (5)는 DSL_SYNTAX.md와 독립 리뷰(modeling-languages.com)가 공통으로 강조하는 ZenUML의 핵심 강점(중괄호 중첩이 PlantUML의 activate/deactivate보다 간결함)을 실제로 활용하기 위함이다.
- **Alternatives considered**: 체크리스트를 생략하고 SKILL.md 지침 문장만으로 대체(리서치에서 확인된 "프롬프트만으로는 fluff가 완전히 안 없어진다"는 근거와 상충하므로 기각); 훨씬 세분화된 10개 이상 항목 체크리스트(Anthropic의 간결성 원칙과 concept.md의 "체크리스트를 과도하게 정교화하지 말라"는 rabbit hole 경고에 위배되어 기각).

## Decision: 자기검증 워크플로 패턴

- **Decision**: Anthropic 가이드의 "generate → validate → fix" 피드백 루프 패턴을 그대로 채택한다 — SKILL.md에 체크리스트를 복사해 진행 상황을 표시하는 워크플로 섹션을 두고, 초안 생성 → 체크리스트 대조 → (위반 시) 수정 → 재확인 순서를 명시한다.
- **Rationale**: 코드 실행이 없는 순수 Markdown 지침 skill이므로 스크립트 기반 검증(`validate.py` 등)은 적용 대상이 아니다. 대신 "참조 문서와 대조하며 사람이 체크하듯 확인"하는 워크플로 패턴(Anthropic 가이드의 "스타일 가이드 준수" 예시와 동일 유형)을 사용한다.
- **Alternatives considered**: 별도 검증 스크립트 작성(이 skill에는 실행 코드가 전혀 없어 범위 밖 — concept.md Option C의 "렌더링 통합"과 같은 rabbit hole로 이어질 위험).

## Decision: 모호한 입력 처리

- **Decision**: 정보가 부족하면 조용히 가정하지 않고 사용자에게 구체적 질문을 한다(spec.md FR-007). 다만 사소한 세부사항(예: 참가자 표시 이름의 대소문자)까지 매번 묻지는 않고, "누가 누구를 호출하는가", "어떤 조건에서 분기하는가"처럼 다이어그램의 정확성에 직접 영향을 주는 정보에 한해서만 질문한다.
- **Rationale**: spec.md Assumptions — 대화형 Claude Code 세션이므로 되묻는 것이 자연스러운 기본 동작이다. 동시에 Anthropic 가이드의 "Claude는 이미 똑똑하다" 원칙에 따라, 하나부터 열까지 다 묻지 않고 다이어그램 정확성에 실질적으로 영향을 주는 것만 추려 질문한다.
- **Alternatives considered**: 항상 최선의 추정으로 채우고 가정을 별도로 명시(정확성 목표 SC-001/SC-004와 정면으로 상충하므로 기각).

## Decision: 라이선스 고지 위치와 형식

- **Decision**: `references/syntax.md` 최상단에 "이 문서는 mermaid-js/zenuml-core의 `docs/DSL_SYNTAX.md`(MIT License)를 재구성한 것입니다"라는 한 줄짜리 고지와 원본 GitHub 링크를 남긴다.
- **Rationale**: spec.md FR-009, `.specify/assessments/zenuml-skill/research.md`의 Data & Constraints에서 이미 방향이 정해졌다 — MIT는 재배포 시 저작권/라이선스 고지 유지를 요구한다.
- **Alternatives considered**: SKILL.md에만 고지(참조 파일이 SKILL.md 없이 단독으로 열람될 수도 있으므로 원본 파일 자체에 고지를 남기는 쪽이 더 안전).

## Decision: 평가(evaluation) 방식

- **Decision**: 자동화 테스트 스위트 대신, spec.md의 User Story 1~3과 Edge Case를 커버하는 대표 프롬프트 시나리오를 `quickstart.md`에 정의하고 수동 실행으로 검증한다.
- **Rationale**: Anthropic 가이드는 "문서를 길게 쓰기 전에 평가부터 만들라"고 권장하며, 이 skill은 실행 코드가 없어 pytest류 자동화가 적용되지 않는다. spec.md의 SC-001~SC-004가 이미 측정 가능한 기준으로 정의되어 있으므로, 이를 검증하는 시나리오만 정의하면 충분하다.
- **Alternatives considered**: 자동화된 골든 파일 비교 스크립트 작성(실행 코드/의존성이 생겨 concept.md Option A/B의 "small~medium appetite" 범위를 벗어남 — 필요해지면 후속 반복에서 고려).

## Decision: 미리보기 전달 메커니즘

- **Decision**: 생성된 ZenUML 원문을 Mermaid `zenuml` 코드펜스에 그대로 담아, 저장소의 `.zenuml/` 아래 파일로 저장하고, 채팅 응답에는 코드 없이 그 파일을 가리키는 상대 경로 링크만 남긴다. 번역이 필요 없다 — 파일 자체가 원문이자 렌더링 가능한 미리보기다.
- **Rationale**: 처음엔 Claude Artifact로 발행하는 방식을 택했으나(아래 "기각된 대안" 참조), 실사용 중 **Artifact를 발행하면 클라이언트가 미리보기 패널을 자동으로 띄우는 동작이 있고 이를 억제할 파라미터가 Artifact 도구에 없다**는 문제가 발견됐다 — 매번 다이어그램을 만들 때마다 원치 않는 팝업이 뜨는 셈이라 사용자 경험상 수용 불가. `AskUserQuestion`으로 발행 여부를 먼저 물어보는 절충안도 검토했으나, 더 근본적인 해결책은 애초에 클라이언트가 자동으로 여는 대상(Artifact)을 쓰지 않는 것이다. 로컬 파일 + 상대 링크는 사용자가 직접 클릭해야만 열리므로 이 문제를 원천적으로 피한다.
  - **정정(2026-07-27)**: 처음엔 "Claude Artifact가 `zenuml` 타입을 렌더링하지 않는다"는 실측 결과를, "일반적인 Mermaid 렌더러 전반이 `zenuml`을 지원하지 않는다"로 성급하게 일반화해 VS Code에서도 `sequenceDiagram`으로 번역하는 방식을 썼다. 이후 VS Code 마크다운 프리뷰(Mermaid Markdown Features)에서 `zenuml` 코드펜스를 직접 렌더링해보니 **정상적으로 도형이 그려지는 것을 실측 확인**했다 — 즉 Claude Artifact만의 제약이었고 VS Code는 애초부터 지원하고 있었다. 이에 따라 번역 단계를 완전히 제거하고 `zenuml` 원문을 그대로 저장하는 방식으로 수정했다. (Claude Artifact가 여전히 `zenuml`을 렌더링하지 않는다는 사실 자체는 변함없음 — 그래서 Artifact 대신 로컬 파일을 쓰는 결정은 그대로 유효하다.)
- **Alternatives considered — 기각된 대안**:
  1. **Claude Artifact 발행** — 처음 채택했으나 자동 팝업 문제로 폐기. (부가로: `zenuml` 코드펜스를 그대로 발행하면 도형이 아닌 원문 텍스트로 표시됨을 실측 확인 — `zenuml`은 Mermaid 코어에 없는 외부 플러그인 타입이라 Artifact 환경에 등록돼 있지 않기 때문.)
  2. **`AskUserQuestion`으로 발행 여부를 먼저 확인 후 Artifact 발행** — 클릭 전엔 아무것도 안 열리게 만드는 절충안이었으나, 로컬 파일 방식이 질문 단계 자체를 없애고도 같은 효과를 내므로 더 단순해 폐기.
  3. **CDN으로 `mermaid.js` + `@mermaid-js/mermaid-zenuml` 플러그인을 로드하는 커스텀 HTML 파일** — ZenUML 원문을 번역 없이 그대로 렌더링해볼 수 있는지 시도했으나, 이후 VS Code가 `zenuml`을 네이티브로 지원함이 확인되어 커스텀 HTML 자체가 불필요해짐, 폐기.
  4. **Mermaid `sequenceDiagram`으로 번역** — VS Code가 `zenuml`을 지원하지 않을 것이라는 잘못된 가정 하에 한동안 채택했었으나, 위 "정정" 항목에서 설명한 대로 그 가정이 틀렸음이 실측으로 밝혀져 폐기. 번역 없이 `zenuml` 원문을 그대로 쓰는 현재 방식이 더 정확하고 단순함.
  5. `app.zenuml.com` 직접 링크 — 불가능(임베드가 `postMessage` 기반).
  6. `mermaid.live` `#pako:`/`#base64:` 해시 링크 — 정확한 JSON 상태 스키마 미확증으로 기각.
  7. `mermaid.live` `?code=` 원격 URL 로딩 — 매번 저장소에 파일 커밋이 필요해 무거워 기각(참고: 결과적으로 채택한 로컬 파일 방식과 유사한 방향이지만, 외부 서비스에 의존하지 않는 쪽이 더 단순함).

## Decision: 출력 파일 위치와 이름

- **Decision**: 저장소 루트의 `.zenuml/` 디렉터리 아래에 다이어그램 파일을 저장한다. 이 디렉터리는 `.gitignore`에 새 항목으로 추가한다.
- **Rationale**: 이 저장소가 이미 `.claude/`, `.specify/` 같은 점(dot)-프리픽스 툴 디렉터리 컨벤션을 쓰고 있어 `.zenuml/`이 자연스럽게 어울린다. 생성물 디렉터리를 이미 무시되는 다른 디렉터리의 자식으로 배치할 필요는 없다 — `dist/`, `build/`, `out/`, `.next/` 등도 관례적으로 자기 이름을 `.gitignore`에 최상위 항목으로 직접 추가하며, 이미 무시되는 폴더 아래에 중첩시키는 것이 표준 관례는 아니다.
- **Alternatives considered**: 이미 무시되는 폴더(예: 있었다면 `tmp/` 등)의 자식으로 중첩 — 이 저장소엔 애초에 그런 범용 무시 폴더가 없었고, 새 최상위 항목을 추가하는 쪽이 더 명확하고 관례적이라 채택하지 않음.

## Remaining Unknowns

없음 — Technical Context의 모든 항목이 위 결정들로 해소되었다.
