# Concept: 스크립트 기반 Markdown 다이어그램/PDF 변환

- **Slug**: exporting-markdown-diagrams
- **Created**: 2026-08-19
- **Recommended option**: Option B — 번들 스크립트를 가진 온전한 Claude Code 스킬

## Options

### Option A — 스킬 없이 체크인된 스크립트만

- **Sketch**: 저장소에 `mmdc`(mermaid-cli)를 감싸는 작은 npm/셸 스크립트 한두 개만 추가하고(예: `scripts/export-diagram.sh`, `scripts/export-pdf.sh`), 사용법은 README에 명령어로 적어둔다. 사용자가 export가 필요할 때 Claude에게 요청하지 않고 터미널에서 직접 그 스크립트를 실행한다. Claude Code나 SKILL.md는 전혀 관여하지 않는다.
- **Appetite**: small (하루 이내)
- **Trade-offs**: 토큰 비용을 가장 확실하게 0으로 만든다 — 에이전트를 아예 거치지 않으므로 스킬을 통한 오케스트레이션 오버헤드(SKILL.md를 읽고 판단하는 데 드는 소량의 토큰)조차 없다. 하지만 이 저장소의 기존 관례(모든 것을 `.claude/skills/*`의 대화형 스킬로 제공)에서 벗어나며, "`/generating-...`처럼 대화로 요청"하는 자연스러운 사용 흐름을 포기하게 된다. 사용자가 정확한 파일/다이어그램/출력 형식을 스스로 지정해야 하므로, 스킬이 제공했을 판단(어떤 다이어그램인지 찾기, 적절한 출력 형식 선택 등)의 편의가 없다.
- **Rabbit holes**: 스크립트 인자 설계(어떤 파일, 어떤 출력 형식, 배치 처리 여부)가 결국 미니 CLI 도구를 새로 설계하는 일이 되어 "작다"던 애초 appetite를 넘어설 수 있다.

### Option B — 번들 스크립트를 가진 온전한 Claude Code 스킬

- **Sketch**: 이 저장소의 기존 스킬(`generating-zenuml-diagrams`, `generating-architecture-views`)과 같은 형태로 `.claude/skills/exporting-markdown-diagrams/`(가칭)를 만든다. `SKILL.md`는 오케스트레이션만 담당한다 — 대상 파일/다이어그램을 찾고, 원하는 출력 형식(SVG/PNG/PDF)을 판단한 뒤, 번들된 스크립트(`scripts/` 아래의 Node.js 또는 Python 스크립트, 리서치에서 확인한 Anthropic `pdf`/`docx` 스킬과 동일한 패턴)를 Bash로 호출한다. 실제 렌더링/변환 작업은 전부 그 스크립트(내부적으로 `mermaid-cli` 또는 동급 도구 사용)가 수행하며, LLM은 콘텐츠를 판단하거나 생성하지 않는다. 사용자는 다른 스킬과 똑같이 자연어로 요청한다(예: "이 다이어그램 png로 뽑아줘").
- **Appetite**: small — 새 렌더링 로직을 만드는 게 아니라 기존 CLI 도구를 감싸는 것뿐이라 기반은 작다. 다만 "Rabbit holes"에 적은 두 가지(전체 문서 PDF 파이프라인, zenuml 버전 고정)를 제대로 다루려 하면 medium 쪽으로 커질 수 있다.
- **Trade-offs**: 이 저장소의 기존 사용 패턴(대화로 스킬 호출)과 자연스럽게 맞고, Anthropic 자체가 문서 처리 스킬에 대해 실제로 쓰는 검증된 설계(오케스트레이션은 LLM, 변환은 스크립트)를 그대로 따른다. 변환 자체는 결정적이므로 반복 실행 시 결과가 일관된다. 다만 스킬을 읽고 호출을 판단하는 데 드는 소량의 토큰은 여전히 남고(0은 아님), 스킬 하나가 두 가지 다른 산출물(다이어그램 단독 export, 문서 전체 PDF export)을 함께 다루면 두 파이프라인의 복잡도를 함께 짊어지게 된다.
- **Rabbit holes**: (1) 문서 전체 PDF 변환은 2단계 문제다 — Mermaid 펜스를 먼저 렌더링해 이미지로 치환한 뒤 PDF로 만들지, 아니면 Chromium 기반 프리뷰-투-PDF 경로를 통째로 쓸지 설계를 확정해야 한다(research 참고). (2) 이 저장소의 주력 산출물인 `zenuml` 플레이버 다이어그램은 `mermaid-cli`가 특정 버전(2023-08-03 이후) 이상이어야 렌더링되므로, 버전 고정이나 명확한 실패 감지를 넣지 않으면 조용히 깨질 수 있다. (3) `mermaid-cli`의 Puppeteer/Chromium 의존성이 무거워 오프라인/샌드박스 환경에서 첫 실행이 실패하거나 느릴 수 있다.

### Option C — 새로 만들지 않고 기존 VS Code 확장 표준화

- **Sketch**: 새 코드를 전혀 추가하지 않는다. 대신 "Markdown PDF" 또는 "Markdown Preview Enhanced" 같은 기존 VS Code 확장을 설치하도록 README/CLAUDE.md에 안내하고, 우클릭 export를 표준 절차로 문서화한다.
- **Appetite**: small (문서 작업뿐)
- **Trade-offs**: 코드를 전혀 안 만들어도 되고, 이미 검증된 도구를 재사용한다. 하지만 problem.md의 non-goal("대화형/수동 단계가 필요하게 만들지 않는다")과 정면으로 부딪힌다 — 매번 GUI에서 우클릭해야 하므로 스크립트로 자동화하거나 CI에 넣을 수 없다. 더 결정적으로, 이 확장들이 내부적으로 어떤 Mermaid 렌더러를 쓰는지 이번 조사에서 확인하지 못했으므로 `zenuml` 플레이버 다이어그램을 실제로 지원하는지가 불확실하다(mermaid-cli도 2023년까지는 지원하지 않았던 바로 그 문제가 여기서도 재현될 수 있음).
- **Rabbit holes**: 없음(할 일이 거의 없으므로) — 다만 "확인되지 않은 zenuml 호환성"이 나중에 문제로 드러나면 결국 Option B로 다시 돌아와야 할 수 있다.

## Recommendation

**Option B**를 권장한다. problem.md의 목표(변환 단계에서 LLM 추론 제거, 반복 실행 시 일관된 결과, `zenuml`/일반 Mermaid 둘 다 커버)와 non-goal(대화형/수동 단계로 만들지 않기)을 모두 만족하는 유일한 선택지이기 때문이다. Option C는 non-goal을 정면으로 위반하고 zenuml 호환성이 검증되지 않았다. Option A는 토큰 비용은 더 확실히 0으로 만들지만, 이 저장소가 이미 확립한 "스킬로 대화형 호출" 패턴을 버리게 되고, Anthropic 자신의 `pdf`/`docx` 스킬 선례(research 참고)가 보여주듯 "스킬 오케스트레이션 + 스크립트 실행"으로도 토큰 비용을 사실상 무시할 수준으로 낮출 수 있으므로 그 정도 차이를 위해 사용성을 희생할 이유가 약하다.

## Out of Scope (for the recommended option)

- 새 다이어그램 *내용*을 생성하는 것(기존 `generating-zenuml-diagrams`/`generating-architecture-views`의 영역).
- 이 저장소·사용자 외의 팀/커뮤니티를 위한 범용화(문제 정의 자체가 단일 사용자 필요로 한정됨).
- 임의의 오프라인/샌드박스 환경에서 Puppeteer/Chromium 다운로드 없이도 완전히 동작하는 것을 보장하는 일 — problem.md의 미해결 질문으로 남아 있으며, 이번 개념 단계에서는 다루지 않는다.
- Mermaid/ZenUML 계열이 아닌 다른 다이어그램 문법(PlantUML 등) 지원.

## Assumptions to Validate

- 이 필요가 실제로 반복될 만큼 자주 발생해서, 스킬 하나를 유지보수할 가치가 (그냥 매번 에이전트에게 맡기는 것보다) 있다는 것 — 지금까지의 유일한 근거는 발화자 본인의 자기보고뿐이다(research, Users & Demand 참고).
- 대상 실행 환경(이 개발 머신, 그리고 향후 이 스킬을 쓸 다른 환경)에서 Node.js 기반 `mermaid-cli`(및 Puppeteer/Chromium 다운로드)를 실행하는 것이 실제로 받아들여진다는 것.
- "다이어그램 단독 export"와 "문서 전체 PDF export"를 하나의 스킬로 묶는 것이 실제로 사용자가 원하는 것이라는 것(problem.md의 미해결 질문 — 별개의 두 문제로 나눠야 할 수도 있음).
- `mermaid-cli`(또는 동급 도구)의 특정 버전이 `zenuml` 다이어그램을 실제로 문제없이 렌더링한다는 것 — research는 업스트림 수정이 존재함을 확인했을 뿐, 이 환경에 설치될 실제 버전으로 직접 검증하지는 않았다.
