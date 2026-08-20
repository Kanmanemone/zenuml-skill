# 아이디어 리서치: 스크립트 기반 Markdown 다이어그램/PDF 변환 스킬

- **Slug**: exporting-markdown-diagrams
- **Created**: 2026-08-19
- **Evidence confidence (overall)**: medium — 도구/기술 관련 findings는 1차 출처를 직접 확인해 신뢰도가 높지만, 수요 신호는 티켓/세션 기록 없이 자기보고 하나뿐이고, 호환성 관련 핵심 사실 하나(mermaid-cli 최소 필요 버전)는 정확한 버전 번호가 아니라 머지 날짜에만 근거하고 있음.

## Users & Demand

- 유일한 수요 신호는 아이디어 발화자 본인이 과거 여러 세션에 걸쳐 에이전트에게 비공식적으로 반복 요청했다는 것뿐이다("예전 세션에서 여러번 반복된 건데") — [source: 사용자의 intake 진술 | ASSUMPTION] (confidence: low). 이 패턴을 뒷받침하는 티켓·대화 기록·커밋은 없다.
- 저장소 전체의 git 커밋 메시지(`git log --all --grep="pdf\|svg\|png\|export\|convert"`)와 `.claude/`/`specs/` 내용을 이 키워드들로 검색했으나 이 반복된 필요를 문서화한 **기존 커밋이나 spec 산출물은 발견되지 않았다** — 과거 요청들은 순전히 대화 중에만 있었고 공식 문서로 남은 적이 없는 것으로 보인다. — [source: 이번 세션의 로컬 저장소 검색] (confidence: high, 다만 이는 어디까지나 "부정적 결과"다 — 즉 *기록된* 흔적이 없다는 것을 확인해줄 뿐, 요청 자체가 없었음을 증명하지는 않는다)
- 이는 팀/커뮤니티 차원에서 보고된 것이 아니라, 단일 사용자(저장소 소유자)·단일 저장소 차원의 필요다. — [source: 저장소 자체의 `.specify/assessments/`와 `specs/` 히스토리, 전부 한 명의 기여자가 작성함] (confidence: medium)

## Prior Art

- **이 저장소 자체의 `generating-zenuml-diagrams` 스킬이 변환 작업을 명시적으로 범위 밖으로 규정하고 있다**: `.claude/skills/generating-zenuml-diagrams/SKILL.md:158`은 *"Converting an existing Mermaid/PlantUML diagram: out of scope for this skill. Say so; only natural-language process descriptions are supported as input."*(기존 Mermaid/PlantUML 다이어그램을 변환하는 것은 이 스킬의 범위 밖이다. 그렇게 안내하며, 자연어 프로세스 설명만 입력으로 지원한다)라고 명시한다 — 새로 제안된 스킬과 기능적으로 겹치지 않음을 확인해준다. 이는 중복 작업이 아니라 이미 인지되어 있던 깔끔한 공백이다. — [source: 로컬 파일] (confidence: high)
- **Anthropic의 공식 스킬 저작 가이드 자체가 이 아이디어의 핵심 설계 원칙을 직접 뒷받침한다.** `skill-creator` 스킬(Anthropic이 스킬 작성법의 참조로 제공)은 `scripts/` 리소스 타입을 *"결정적/반복적 작업을 위한 실행 코드"*라고 명시적으로 문서화하며, "Progressive Disclosure" 모델에서 스크립트는 "[컨텍스트에] 로드하지 않고도 실행할 수 있다"고 설명한다 — 즉 스크립트를 번들해 Bash로 실행하는 것이 결정적인 변환 작업을 토큰 예산 밖에 두는 공인된 방식이며, 이 아이디어가 요구하는 메커니즘과 정확히 일치한다. — [source: https://github.com/anthropics/skills (raw: `skills/skill-creator/SKILL.md`), host: raw.githubusercontent.com, policy: allowlisted (GitHub이 호스팅하며 github.com과 동일한 신뢰 등급)] (confidence: high)
- **Anthropic의 실제 프로덕션 `pdf` 스킬이 바로 이런 방식으로 만들어진 문서 처리 스킬의 직접적 선례다**: `skills/pdf/SKILL.md`는 바로 실행 가능한 Python 스니펫(`pypdf`, `pdfplumber`, `reportlab`)과 CLI 도구(`pdftotext`, `qpdf`, `pdftk`)를 모아둔 참조 가이드이며, 스킬 폴더에는 추론을 거치지 않고 바로 호출하도록 만들어진 독립 스크립트(`skills/pdf/scripts/convert_pdf_to_images.py`, `check_bounding_boxes.py` 등)도 함께 번들되어 있다. 같은 저장소의 `docx`, `pptx`, `xlsx`에도 동일한 패턴이 있다. — [source: https://github.com/anthropics/skills, host: github.com / raw.githubusercontent.com / api.github.com, policy: allowlisted] (confidence: high)
- **`mermaid-cli`(`mmdc`, `@mermaid-js/mermaid-cli`)는 이 아이디어의 "다이어그램 변환" 절반에 대해 이미 확립된, LLM을 쓰지 않는 도구다.** `.mmd` 파일이나 mermaid 코드 펜스가 포함된 Markdown 파일을 CLI 호출 한 번(`mmdc -i in.md -o out.svg`)으로 SVG/PNG/PDF로 바로 렌더링하며, 테마/배경/스케일 플래그를 지원하고, 전역 설치 없이 `npx -p @mermaid-js/mermaid-cli mmdc -h`로도 쓸 수 있다. — [source: npm/GitHub 문서, 웹 검색으로 취합 — https://github.com/mermaid-js/mermaid-cli, host: github.com, policy: allowlisted] (confidence: high)
- **브라우저 없이 동작하는 순수 Python 대안도 존재한다**(`mermaidx` — Node.js/Puppeteer/실제 브라우저 대신 QuickJS + resvg를 내장) — 나중에 스킬이 `mermaid-cli`가 끌어오는 Chromium 다운로드를 피하고 싶어질 경우 참고할 만하다. — [source: https://github.com/MohammadRaziei/mermaidx, host: github.com, policy: allowlisted, 웹 검색으로 발견] (confidence: medium — 검색으로 찾았을 뿐, 저장소를 직접 fetch해 검증하지는 않음)

## Market & Context

- **이 저장소의 README가 이미 의존하고 있는 VS Code 내장 Mermaid 프리뷰에는 export 기능이 없다** — 이 저장소의 README는 프로젝트가 보기 용도로 "VS Code 내장 Mermaid 프리뷰"에 의존한다고 설명하지만, 그 프리뷰만으로는 이미지/PDF를 저장할 수 없다. 별도 단계가 필요하며, "매번 agent보고 알아서 하라고 요청"한 것은 아마 이 단계를 대신한 것으로 보인다. — [source: 이 저장소의 `README.md`/`README.ko.md`, "How to use"/"사용법" 절] (confidence: high)
- **대화형 사용을 위한 노코드 대안은 이미 존재한다**: "Markdown PDF", "Markdown Preview Enhanced" 같은 VS Code 확장 프로그램들은 내부적으로 headless Chrome을 써서 Markdown 파일(렌더링된 Mermaid 포함)을 우클릭 한 번으로 PDF/PNG로 export해준다 — 이는 shape 단계에서 이 아이디어와 견주어봐야 할 실제 "아무것도 안 만들었을 때의 대안"이다: 이게 정말 Claude Code *스킬*이어야 하는가, 아니면 이미 설치돼 있거나 설치 가능한 이런 확장 중 하나를 문서화/표준화하는 것만으로 새 스크립트 번들 없이도 "일관성" 요구가 충족되는가? — [source: VS Code 확장 생태계에 대한 일반 지식 — 이번 세션에서 별도로 재검증하지 않음] (confidence: low, 결정 전에 확인해볼 가치가 있다고 표시)

## Data & Constraints

- **이 머신에는 이미 Node.js v24.19.0, npm 11.17.0, Python 3.14.6이 있지만 `pandoc`은 없다.** — [source: `node --version` / `npm --version` / `python --version` / `pandoc --version`, 이번 세션에서 로컬 실행] (confidence: high). 이는 "추가 설치 없이 그냥 동작함"을 원한다면 Pandoc 기반 파이프라인보다 Node 기반(`mermaid-cli`) 또는 Python 기반 파이프라인에 유리하다 — Pandoc을 문서화된 전제조건으로 일부러 추가하지 않는 한 그렇다.
- **이 저장소의 주력 다이어그램 산출물은 `zenuml` 플레이버 Mermaid다**(`generating-zenuml-diagrams`가 만듦), 일반 flowchart/sequence Mermaid가 아니다. 순정 `mermaid-cli`는 과거에 `zenuml` 다이어그램 타입 자체를 전혀 인식하지 못했다: 등록된 이슈 하나가 `mmdc`로 렌더링을 시도했을 때 `Error: ... UnknownDiagramError: No diagram type detected ... for text: zenuml` 오류가 재현되는 것을 보여준다. — [source: https://github.com/mermaid-js/mermaid-cli/issues/564, host: github.com, policy: allowlisted] (confidence: high)
- **그 공백은 업스트림에서 이미 고쳐졌다**: [PR #566](https://github.com/mermaid-js/mermaid-cli/pull/566)이 `mindmap` 지원을 추가했던 것과 같은 방식으로 `mermaid-cli`에 네이티브 `zenuml` 지원을 추가했고, **2023-08-03**에 머지됐으며 이후로는 별도의 Puppeteer 설정이나 CLI 플래그가 필요 없다 — 번들 렌더러 크기가 약 700KB(gzip 약 200KB) 늘고 빌드 시간이 약 2.5초 늘어난다. — [source: https://github.com/mermaid-js/mermaid-cli/pull/566, host: github.com, policy: allowlisted] (confidence: *이 수정이 실제로 존재하고 별도 설정이 필요 없다*는 점은 high; *정확한 최소 npm 버전*은 medium — PR 기록은 버전 번호가 아니라 머지 날짜만 알려주므로, 스킬은 "최신 버전이면 항상 동작한다"고 가정하지 말고 2023-08-03 이후에 릴리스된 `mermaid-cli` 버전을 고정/확인해야 한다).
- **이 저장소의 `generating-architecture-views` 스킬은 일반 Mermaid `flowchart` 다이어그램도 만든다**(`%%{init}%%` 스타일 블록 포함, 그리고 이번 세션의 `FR-007b`에 따라 선택적으로 `defaultRenderer: elk`도 포함) — 이는 표준 Mermaid이므로 위의 `zenuml` 플러그인 관련 위험이 전혀 없다.

## Evidence Against the Idea

- **근본 문제 자체가 온전한 "스킬"까지는 필요 없을 수 있다.** 진짜 아픈 지점이 "에이전트가 매번 결정적인 변환을 다시 하느라 토큰을 태운다"는 것이라면, 문서화된 CLI 명령어 하나(또는 사용자가 Claude를 아예 거치지 않고 직접 실행하는, 저장소에 체크인된 작은 npm/셸 스크립트)가 Claude Code 스킬보다 더 직접적으로 토큰 비용을 *0*으로 만든다 — 스킬은 Claude가 `SKILL.md`를 읽고 스크립트를 호출하기로 판단하는 데 여전히 약간의 토큰이 든다. (어떤 파일/다이어그램인지, 출력 형식은 무엇인지, 배치 처리를 할지 등에 대한) 판단이 필요한 온전한 스킬이 정말 필요한지, 아니면 사용자가 직접 실행하는 평범한 스크립트로 충분한지는 `/speckit-assess-shape`에서 다뤄야 할 열린 설계 질문이며, 이 아이디어만으로는 아직 정해지지 않았다.
- **단일 사용자, 낮은 빈도의 수요다**(Users & Demand 참고) — 이 필요가 여러 세션에 걸쳐 몇 번 요청한 그 한 사람을 넘어선다는 증거는 없다. 노력 대비 가치 비율은 전적으로 그 요청이 앞으로 얼마나 자주 반복되느냐에 달려 있는데, 이는 어디에도 측정돼 있지 않다.
- **`mermaid-cli`의 Puppeteer/headless-Chromium 의존성은 무겁다**(실제 브라우저 다운로드로, `npx`를 처음 실행할 때 역사적으로 200~300MB 이상이었다) — 제약이 있거나 샌드박스화되었거나 오프라인인 환경에서는 느리거나 아예 막힐 수 있다 — 이 아이디어가 암시하는 "그냥 잘 동작한다"는 목표에 위험 요소다.
- **문서 전체의 Markdown→PDF 변환은 다이어그램→이미지 변환 하나보다 엄밀히 더 어려운, 2단계짜리 문제다**: 순진한 Markdown→PDF 변환기(예: Pandoc)는 Mermaid 코드 펜스를 이해하지 못하므로, PDF 변환 전에 다이어그램을 먼저 별도로 렌더링해 문서를 이미지 참조로 다시 써야 하거나(또는 파일 전체를 Chromium 기반 Markdown-프리뷰-투-PDF 경로로 흘려보내야) 한다 — 이는 이 아이디어의 어느 한쪽 절반만 놓고 봤을 때보다 움직이는 부품이 의미 있게 더 많고, 기존의 올인원 VS Code 확장(Market & Context 참고)이 새 도구 없이도 이미 "충분히 괜찮을" 수 있는 지점이다.
- **버전 드리프트 위험**: `mermaid-cli`의 `zenuml` 지원이 비교적 최근(2023년) 추가된 것이므로, 미래의 어느 머신에 이미 전역 설치돼 있는 더 오래된 `mmdc`가 이번 조사에서 재현한 것과 동일한 `UnknownDiagramError`로 다시 조용히 실패할 수 있다 — 스킬은 버전을 고정하거나, 아니면 이 실패 모드를 영원히 해결됐다고 가정하지 않고 명확히 감지/보고해야 한다.

## Gaps & Open Questions

- [NEEDS CLARIFICATION: 이 스킬이 진짜 "스킬"(SKILL.md + 에이전트 오케스트레이션)이어야 하는가, 아니면 그냥 리포에 체크인된 npm/셸 스크립트 한두 개로 충분한가 — Users & Demand, Evidence Against #1 참고]
- [NEEDS CLARIFICATION: `.zenuml/*.md`(zenuml 플레이버) 산출물과 architecture-view의 일반 Mermaid `flowchart` 산출물을 하나의 스킬이 동일한 방식으로 다뤄도 되는가, 아니면 서로 다른 처리(zenuml은 mermaid-cli 최소 버전 확인 필요)가 필요함을 사용자에게 명시해야 하는가]
- [NEEDS CLARIFICATION: 전체 md→PDF 변환에서 임베드된 다이어그램을 실제로 어떻게 다룰지(2단계 파이프라인 vs Chromium 기반 프리뷰 인쇄) — 이 조사에서 기술적으로 가능한 두 경로만 확인했고 사용자의 선호는 아직 모름]
- [NEEDS CLARIFICATION: Puppeteer/Chromium 다운로드가 발생해도 괜찮은 환경인지(오프라인/샌드박스 제약 여부)]
- [NEEDS CLARIFICATION: VS Code의 "Markdown PDF"/"Markdown Preview Enhanced" 같은 기존 확장 프로그램을 그냥 문서화/표준화하는 것으로 "일관성" 요구가 이미 충족되는 건 아닌지 — 사용자가 실제로 원하는 건 GUI 없는 headless 변환(CI 등)인지 확인 필요]

## Sources

- https://github.com/anthropics/skills (host: github.com, policy: allowlisted)
- https://raw.githubusercontent.com/anthropics/skills/main/skills/pdf/SKILL.md (host: raw.githubusercontent.com, policy: allowlisted)
- https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md (host: raw.githubusercontent.com, policy: allowlisted)
- https://api.github.com/repos/anthropics/skills/contents/skills/pdf/scripts (host: api.github.com, policy: allowlisted)
- https://github.com/mermaid-js/mermaid-cli/issues/564 (host: github.com, policy: allowlisted)
- https://github.com/mermaid-js/mermaid-cli/pull/566 (host: github.com, policy: allowlisted)
- https://github.com/mermaid-js/mermaid-cli (host: github.com, policy: allowlisted, 웹 검색으로 발견)
- https://github.com/MohammadRaziei/mermaidx (host: github.com, policy: allowlisted, 웹 검색으로 발견)
- Local: 이 저장소 자체의 git 히스토리와 `.claude/skills/generating-zenuml-diagrams/SKILL.md` (읽기 전용, fetch 없음)
- Local: 이번 세션 셸에서 실행한 `node --version`, `npm --version`, `python --version`, `pandoc --version`
