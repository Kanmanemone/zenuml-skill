# 아이디어 인테이크: 스크립트 기반 Markdown 다이어그램/PDF 변환 스킬

- **Slug**: exporting-markdown-diagrams
- **Created**: 2026-08-19
- **Source**: 붙여넣은 텍스트
- **Type**: new-capability

## Idea (as captured)

> 예전 세션에서 여러번 반복된 건데, md 파일 속 다이어그램을 svg 또는 png로 변환하거나 md 파일을 통째로 pdf로 변환하는 스킬을 만들고 싶어. 토큰 낭비 없이 스크립트로만 변환될 수 있게 하고싶어. 지금까지는 agent보고 알아서 하라고 매번 요청했기 때문에 그 때마다 토큰이 소모되었거든. 또, 이번에 만들 스킬로 일관성까지도 갖추고 싶고.

## Restated

사용자는 마크다운 파일 안에 있는 다이어그램(예: Mermaid)을 SVG 또는 PNG로 변환하거나, 마크다운 파일 전체를 PDF로 변환하는 새 Claude Code 스킬을 만들고 싶어 한다. 매번 에이전트(LLM)에게 변환 작업을 맡겨 토큰을 소모하는 대신 순수 스크립트 실행만으로 변환이 끝나기를 원하며, 이를 통해 변환 결과의 일관성도 함께 확보하고자 한다.

## Origin & Context

- **Raised by**: [NEEDS CLARIFICATION: 발화자가 이 저장소의 소유자로 보이나, 구체적 이름/역할은 이번 입력만으로 확인 불가]
- **Trigger**: "예전 세션에서 여러 번 반복된" 패턴 — 과거 여러 세션에서 md 속 다이어그램이나 문서 전체를 이미지/PDF로 바꿔달라고 에이전트에게 매번 개별 요청했고, 그때마다 토큰이 소모된 것이 계기. 구체적으로 어떤 세션/어떤 산출물에서 이 반복이 있었는지는 [NEEDS CLARIFICATION: 특정 세션·파일 사례 미상]

## First-Glance Unknowns

- [NEEDS CLARIFICATION: 변환 대상 다이어그램 문법이 Mermaid만인가, 이 저장소의 다른 스킬이 다루는 ZenUML 등도 포함하는가?]
- [NEEDS CLARIFICATION: "스크립트로만 변환"의 구체적 실행 수단은 무엇을 염두에 두는가 — 예: mermaid-cli(mmdc) 같은 Node.js CLI, Python 라이브러리, 또는 별도 설치가 필요한 외부 바이너리까지 허용하는가?]
- [NEEDS CLARIFICATION: md → PDF 변환 시 문서에 임베드된 다이어그램도 함께 렌더링돼야 하는가, 아니면 다이어그램을 먼저 SVG/PNG로 추출한 뒤 그 결과물을 PDF에 포함하는 2단계 파이프라인을 원하는가?]
- [NEEDS CLARIFICATION: 이 저장소의 기존 두 스킬(`generating-zenuml-diagrams`, `generating-architecture-views`)이 만드는 `.zenuml/*.md` 산출물이 주 대상인가, 아니면 저장소 내 임의의 모든 `.md` 파일을 대상으로 하는 범용 스킬인가?]
- [NEEDS CLARIFICATION: "일관성"이 구체적으로 가리키는 문제가 무엇인가 — 매번 에이전트가 다른 도구/스타일로 변환해 결과물이 들쭉날쭉했다는 뜻인지, 다른 의미인지?]
- [NEEDS CLARIFICATION: 실행 환경에 Node.js/Python 등 필요한 런타임이 이미 설치돼 있다고 가정해도 되는가, 아니면 스킬이 설치 여부 확인/안내까지 책임져야 하는가?]
