# Decision: 스크립트 기반 Markdown 다이어그램/PDF 변환

- **Slug**: exporting-markdown-diagrams
- **Decided**: 2026-08-19
- **Verdict**: go
- **Artifacts reviewed**: intake.md, research.md, problem.md, concept.md

## Scorecard

| Criterion | Rating | Justification |
|-----------|--------|---------------|
| Problem validity | adequate | 반복되는 실제 아픈 지점(결정적 작업에 LLM 추론을 쓰는 토큰 낭비 + 결과 불일치)이지만, 재발 빈도를 뒷받침하는 기록된 증거는 없고 발화자 본인의 자기보고뿐이다(research, Users & Demand). |
| Evidence strength | adequate | 기술적/실현가능성 증거는 강하다 — Anthropic 자신의 `pdf`/`docx` 스킬 선례, `mermaid-cli`의 실제 동작, `zenuml` 호환성 이슈+수정 커밋까지 1차 출처로 직접 확인함. 다만 "수요"(얼마나 자주 반복될지) 쪽 증거는 약하며 이는 명확히 인지하고 넘어간다 — 아래 Verdict & Rationale 참고. |
| Value vs. inaction | adequate | 해결 시 토큰 낭비·불일치가 사라지지만 정확한 재발 빈도가 없어 가치를 정량화할 수 없다. 다만 concept.md의 권장안이 small appetite라 비용이 낮으므로, 적당한 재발 빈도만 있어도 "아무것도 안 하는 것"보다 나을 가능성이 높다. |
| Feasibility / appetite | strong | concept.md의 Option B가 이 저장소의 기존 두 스킬과 Anthropic 자신의 `pdf`/`docx` 스킬이라는 검증된 패턴을 그대로 따르는 구체적이고 신뢰할 수 있는 설계를 제시한다. 새 렌더링 로직이 아니라 기존 CLI 도구를 감싸는 정도라 기술적 위험이 낮다. |
| Strategic fit | strong | 비준된 constitution은 없지만, 이 저장소는 이미 반복 작업을 Claude Code 스킬(`generating-zenuml-diagrams`, `generating-architecture-views`)로 캡슐화하는 뚜렷한 자체 방향성을 가지고 있고, 이 아이디어는 그 두 스킬의 산출물을 직접 다루는 자연스러운 세 번째 축이다. |
| Risk posture | adequate | concept.md의 "Rabbit holes"가 주요 위험(전체 문서 PDF의 2단계 파이프라인, zenuml 버전 고정, Puppeteer/Chromium 무게)을 구체적 완화 경로와 함께 이미 짚어뒀다. 다만 그 완화책들이 아직 실제로 검증되지는 않았다(예: 정확한 mermaid-cli 최소 버전을 이 환경에 직접 설치해 확인하지 않음). |

## Verdict & Rationale

**go.** Problem validity와 Value vs. inaction은 "adequate"에 그치는데, 이는 재발 빈도를 뒷받침하는 기록이 없기 때문이다 — 하지만 이 아이디어는 이례적으로, 수요를 보고한 사람과 빌드 여부를 승인하는 사람이 동일인(저장소 소유자 1인)이므로, 자기보고 수요를 다수 이해관계자 대상 제품 아이디어와 같은 엄격도로 요구할 이유가 약하다. Evidence strength는 "adequate"로 판정했다 — 수요 쪽 증거는 약하지만 실현가능성/기술 쪽 증거(Anthropic 자신의 스킬 설계 선례, mermaid-cli의 실제 동작과 zenuml 호환성 수정 이력까지 1차 출처로 직접 확인)가 강해서, 종합적으로 "weak"나 "unknown"으로 깎아내릴 근거는 없다. Feasibility와 Strategic fit이 모두 strong이고, 권장 옵션의 appetite가 작으며(비용이 낮음), 이미 신뢰할 수 있는 설계 패턴을 그대로 재사용할 수 있으므로, 얕은 수요 증거를 감수하고도 명세 단계로 넘길 만한 낮은 리스크·낮은 비용의 아이디어라고 판단한다.

## If go — Handoff to `/speckit-specify`

- **Problem**: 저장소 소유자가 Markdown 산출물(다이어그램, 문서 전체)을 이미지/PDF로 export하고 싶을 때마다 매번 에이전트에게 추론시켜야 해서 토큰이 낭비되고 결과가 일관되지 않다.
- **Chosen approach**: concept.md Option B — 번들 스크립트를 가진 온전한 Claude Code 스킬. `SKILL.md`는 오케스트레이션(대상 파일/다이어그램 판단, 출력 형식 결정, 스크립트 호출)만 담당하고, 실제 렌더링/변환은 번들된 스크립트(`mermaid-cli` 등을 감싼 Node.js/Python 스크립트)가 전담해 LLM 추론 없이 결정적으로 수행한다.
- **In scope**: (a) `.md` 파일에 임베드된 Mermaid/ZenUML 다이어그램을 SVG 또는 PNG로 변환, (b) `.md` 파일 전체를 PDF로 변환. 이 저장소의 두 다이어그램 유형(zenuml 플레이버 시퀀스 다이어그램, 일반 Mermaid `flowchart`) 모두 지원.
- **Out of scope**: 새 다이어그램 내용 생성(기존 두 스킬의 영역), Mermaid/ZenUML 계열이 아닌 다이어그램 문법(PlantUML 등), 이 저장소·사용자를 넘어선 범용화, 오프라인/샌드박스 환경에서 Puppeteer/Chromium 없이 완전히 동작하는 것의 보장.
- **Success metrics**: 변환 단계 자체에 LLM 추론이 필요 없음(오케스트레이션만 소량의 토큰 사용); 동일 입력을 반복 변환하면 매번 동일한 결과; `.zenuml/*.md`의 zenuml 플레이버 다이어그램이 일반 flowchart와 마찬가지로 실패 없이 변환됨.
- **Carried-forward open questions**:
  - [NEEDS CLARIFICATION: "다이어그램 단독 export"와 "문서 전체 PDF export"를 하나의 스킬로 묶을지, 별개의 두 스킬/기능으로 나눌지]
  - [NEEDS CLARIFICATION: "일관성"의 정확한 측정 기준(동일 출력 재현 vs 스타일 통일 vs 둘 다)]
  - [NEEDS CLARIFICATION: 문서 전체 PDF 변환 파이프라인 설계(다이어그램 선추출+치환 2단계 vs Chromium 기반 프리뷰 인쇄)]
  - [NEEDS CLARIFICATION: 실제 사용할 `mermaid-cli`(또는 동급 도구)의 최소 버전을 이 환경에 설치해 zenuml 렌더링을 직접 검증]
  - [NEEDS CLARIFICATION: 오프라인/샌드박스 환경 지원이 실제로 필요한지]
