# Implementation Plan: Markdown 다이어그램/PDF export 스킬

**Branch**: `004-exporting-markdown-diagrams` | **Date**: 2026-08-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-exporting-markdown-diagrams/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

마크다운 파일 안의 다이어그램(이 저장소의 zenuml 플레이버 시퀀스 다이어그램, 일반 Mermaid flowchart)을 SVG/PNG로, 또는 문서 전체를 PDF로 변환하는 Claude Code Skill(가칭 `exporting-markdown-diagrams`)을 만든다. 스킬 자신(`SKILL.md`)은 오케스트레이션만 담당한다 — 요청에서 출력 형식(SVG/PNG/PDF)과 변환 범위(다이어그램만/문서 전체)를 판단하고, 둘 중 하나 이상이 불분명하면 `AskUserQuestion`으로 확인한 뒤, 실제 변환은 번들된 Node.js 스크립트가 `@mermaid-js/mermaid-cli`(mmdc)를 통해 결정적으로 수행한다. LLM은 변환 대상 내용을 재해석하거나 다시 만들어내지 않는다. 문서 전체 PDF 변환은 mmdc의 markdown→markdown 다이어그램 추출 기능으로 각 다이어그램을 SVG로 먼저 렌더링한 뒤, 그 SVG를 HTML에 인라인으로 삽입하고 헤드리스 브라우저로 PDF 인쇄하여 다이어그램의 텍스트가 선택·복사 가능하게 만든다.

## Technical Context

**Language/Version**: Node.js (이 개발 환경에 이미 설치된 v24.19.0 확인됨; LTS 계열 버전을 전제). 스킬 자체는 001/003과 동일하게 `SKILL.md` 지침 문서이지만, 이번 기능은 그 두 스킬과 달리 실제 실행되는 번들 스크립트를 포함한다.

**Primary Dependencies**: `@mermaid-js/mermaid-cli`(다이어그램 렌더링과 markdown→markdown 다이어그램 추출을 모두 수행), 그 내부 의존성인 Puppeteer(헤드리스 Chromium — 문서 전체 PDF 인쇄에도 재사용), 마크다운→HTML 변환 라이브러리(정확한 선택은 Phase 0 참고).

**Storage**: N/A — 요청받은 위치에 산출물 파일(SVG/PNG/PDF)을 쓰는 것 외 영속 저장소가 없다.

**Testing**: 변환 스크립트 자체는 결정적이므로 유닛 테스트로 검증하기 좋다(입력 다이어그램 → 기대 출력 형식/구조). 스킬 전체의 검증은 001/003과 동일하게 `quickstart.md`의 대표 시나리오를 실행해 확인한다.

**Target Platform**: Claude Code(CLI/IDE) — 이 저장소의 기존 스킬과 동일한 실행 환경. 번들 스크립트는 Node.js가 설치된 사용자 머신에서 실행된다(Windows 포함).

**Project Type**: single — 기존 두 스킬과 나란히 놓이는 단일 Claude Code Skill 모듈(지침 + 번들 스크립트) 추가.

**Performance Goals**: N/A — 대화형 개인 도구로 처리량 목표는 없다. 다만 단일 변환 요청이 사용자가 기다릴 만한 시간(헤드리스 브라우저 기동 포함 수 초~수십 초) 안에 끝나야 한다는 정성적 기대만 있다.

**Constraints**:
- 변환 자체는 LLM 추론이 아니라 결정적 스크립트/도구 실행으로 수행해야 한다(spec.md FR-005).
- 다이어그램 소스에 명시된 렌더러 지정(예: `defaultRenderer`)을 임의로 제거·대체해서는 안 되며, 소스를 있는 그대로 렌더러에 전달해야 한다(FR-004).
- 출력 형식·변환 범위 중 불분명한 항목만 `AskUserQuestion`으로 확인하며, 둘 다 불분명하면 하나의 상호작용으로 함께 물어야 한다(FR-001~003).
- 문서 전체 PDF 변환 시 포함된 다이어그램은 래스터가 아니라 벡터(SVG)로 삽입되어 텍스트가 선택·복사 가능해야 한다(FR-007).
- 이 저장소의 두 다이어그램 유형(zenuml 플레이버, 일반 Mermaid flowchart) 모두 지원해야 한다(FR-006).
- 모든 산출물은 원본 마크다운과 같은 디렉토리가 아니라 그 아래의 전용 하위 디렉토리(`exports/`)에 생성되어야 하며, 그 디렉토리가 없으면 자동으로 만들어져야 한다(FR-009~012).
- PNG 변환은 가로·세로 픽셀 크기를 고정값으로 지정하지 않고, 고정된 해상도 배율(mermaid-cli `--scale`, 즉 Puppeteer `deviceScaleFactor`)로 다이어그램의 실제 레이아웃 크기에 맞춰 픽셀 수가 정해져야 한다(FR-013).

**Scale/Scope**: 단일 사용자(저장소 소유자), 파일 하나 단위의 변환 요청. 대량 배치 처리, 팀/커뮤니티 배포, Mermaid/ZenUML 이외의 다이어그램 문법, 완전한 오프라인 지원은 범위 밖이다(spec.md Assumptions).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`는 아직 `[PROJECT_NAME]` 등 템플릿 placeholder 상태이며 비준된 원칙이 없다 — 대조할 공식 게이트가 존재하지 않는다. 이번 계획 단계에서는 Constitution Check를 **적용 불가(N/A)** 로 처리하고 위반 사항 없음으로 진행한다.

**Post-Phase 1 재확인**: Phase 1 설계(data-model.md, contracts/, quickstart.md) 완료 후에도 constitution이 여전히 placeholder 상태임을 재확인함 — 상태 변화 없음, 게이트 여전히 N/A.

## Project Structure

### Documentation (this feature)

```text
specs/004-exporting-markdown-diagrams/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── skill-interface.md
├── checklists/
│   └── requirements.md  # /speckit-specify output
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
.claude/skills/exporting-markdown-diagrams/
├── SKILL.md               # 워크플로: 요청에서 형식/범위 판단 → 불분명하면 AskUserQuestion(최대 2문항) → 번들 스크립트 호출 → 산출물 경로 제시
└── scripts/
    ├── export-diagrams.js   # 범위="다이어그램만": mmdc를 호출해 SVG/PNG/PDF로 변환(다이어그램이 여러 개면 mmdc 자체의 번호 매김 기능을 그대로 사용)
    ├── export-document-pdf.js  # 범위="문서 전체": mmdc의 md→md 다이어그램 추출로 SVG 생성 → HTML 변환 시 SVG 인라인 삽입 → Puppeteer page.pdf()로 인쇄
    └── lib/
        ├── inline-svg.js    # 중간 산출물(마크다운 속 이미지 참조)의 SVG 파일 내용을 HTML에 인라인으로 치환하는 공용 로직
        ├── run-mmdc.js      # 두 스크립트가 공유하는 mmdc 호출 헬퍼 — mermaid-cli의 JS 엔트리포인트를 Node로 직접 실행해 Windows의 `.cmd` 셰임 spawn 문제(EINVAL)를 피함(구현 중 발견, `/speckit-converge` T022로 문서화)
        └── export-dir.js    # 두 스크립트가 공유하는 출력 디렉토리 헬퍼 — 원본 마크다운 경로 → `<그 디렉토리>/exports`를 계산하고 없으면 생성(FR-009~010)
```

**Structure Decision**: 이 기능은 이 저장소의 기존 두 스킬(`generating-zenuml-diagrams`, `generating-architecture-views`)과 동일하게 `.claude/skills/<name>/` 아래 `SKILL.md` + 보조 코드로 구성되는 단일 skill 모듈이다. 다만 앞의 두 스킬과 달리 `references/`(참조 문서)가 아니라 `scripts/`(실행 코드)를 번들한다 — Anthropic 자신의 `pdf`/`docx` 스킬이 쓰는 패턴과 같다(평가 단계 `research.md` 참고). 전통적인 애플리케이션의 "Option 1/2/3" 소스 구조는 적용되지 않는다.

## Complexity Tracking

*No constitution violations to justify — Constitution Check is N/A (no ratified constitution). This section is intentionally empty.*
