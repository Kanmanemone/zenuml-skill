# Implementation Plan: 다이어그램별 개선 이력 로깅

**Branch**: `002-diagram-feedback-log` | **Date**: 2026-07-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-diagram-feedback-log/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`generating-zenuml-diagrams`를 확장해, 확인 질문이나 선택 UI 없이 대화의 자연스러운 흐름만으로 다이어그램 이력을 관리한다. 핵심은 **워크플로 맨 앞에 오는 요청 종류 판단 절차**다 — 다이어그램을 만들기 전에 먼저 이 요청이 (1) 방금 만든 다이어그램에 대한 재생성 요청인지, (2) 완전히 새로운 다이어그램 요청인지, (3) 새 요청인데 slug가 우연히 기존 파일과 겹치는 경우인지를 판정한다. 판정 결과에 따라 동작이 완전히 갈린다 — 재생성이면 다이어그램 산출물 파일(`.zenuml/<slug>.md`)을 새 내용으로 통째로 교체하고 별도 로그 파일(`.zenuml/log/<slug>.md`)에는 이번 요청·응답을 라운드로 이어붙이며, 최초 생성(또는 slug 충돌로 인한 새 요청)이면 두 파일을 각각 새로 만든다. 판단이 애매하면 추측하지 않고 feature 001의 기존 "명확화 질문" 패턴을 재사용해 되묻는다. 로그 파일은 `.zenuml/` 하위라 기존 gitignore 규칙을 그대로 물려받아 기본적으로 버전관리 대상이 아니며, 어떤 작업이 특정 로그 파일을 실제로 인용할 때만 그 파일 하나를 `git add -f`로 선별 스테이징한다 — 이 컨벤션은 `SKILL.md` 자체에 문서화하고 다른 Spec Kit 스킬 파일은 건드리지 않는다.

## Technical Context

**Language/Version**: N/A — 실행 코드가 없는 Markdown 기반 Skill. 기존 `.claude/skills/generating-zenuml-diagrams/SKILL.md`를 확장하며 새 skill을 만들지 않는다.

**Primary Dependencies**: 없음 — 외부 라이브러리/런타임 의존성 없음. 확인 질문·선택 UI(AskUserQuestion 등)를 전혀 쓰지 않는다 — 이번 설계의 핵심 결정.

**Storage**: 영속 데이터베이스는 없음. 다이어그램 산출물은 feature 001이 이미 쓰는 `.zenuml/<slug>.md`(재생성 시 전체 교체), 개선 이력은 새 위치 `.zenuml/log/<slug>.md`(재생성마다 append)에 각각 마크다운으로 저장한다. 두 경로 모두 기존 `.zenuml/` gitignore 규칙(`.gitignore:10`)에 포함되어 새 gitignore 항목이 필요 없다(research.md, Decision: 로그 파일 위치).

**Testing**: 자동화된 테스트 프레임워크 없음(코드가 없으므로). feature 001과 동일하게 evaluation-driven 접근을 따라, spec.md User Story 1~4와 Edge Case, 그리고 이번 설계의 핵심인 "요청 종류 판단"을 커버하는 대표 시나리오를 `quickstart.md`에 정의하고 수동으로 실행해 성공 기준(SC-001~SC-005) 충족 여부를 검증한다.

**Target Platform**: Claude Code (CLI/IDE) — 기존 `.claude/skills/generating-zenuml-diagrams`와 동일한 실행 환경.

**Project Type**: single — 기존 skill 하나를 확장하는 것이며 별도 프론트엔드/백엔드 구분이 없다.

**Performance Goals**: N/A — 런타임 서비스가 아니다. 인용 감지는 에이전트가 이미 읽기로 한 로그 파일에 결부된 결정론적 동작(git 명령 1회)이어야 하며 로그 전체를 매번 다시 스캔하는 방식은 피한다(research.md, Decision: 인용 시 선별 스테이징).

**Constraints**:
- **요청 종류 판단(최초 생성 / 재생성 / slug 충돌로 인한 새 요청)은 다이어그램을 만들기 전, 워크플로의 가장 첫 단계여야 한다** — 사용자가 명시적으로 요구한 우선순위. 이 판단을 건너뛰거나 뒤로 미루면 엉뚱한 파일을 덮어쓰거나 로그를 잘못된 다이어그램에 이어붙이는 되돌리기 어려운 실수로 이어질 수 있다(spec.md Edge Cases).
- 확인 질문이나 선택 UI는 전혀 사용하지 않는다 — 재생성 여부는 대화 맥락으로 판단하고, 판단이 애매할 때만 feature 001의 기존 "명확화 질문" 패턴을 재사용해 되묻는다(spec.md FR-002, Edge Cases).
- 다이어그램 산출물(`.zenuml/<slug>.md`)은 재생성마다 전체 교체된다 — 과거 버전은 그 파일에 남지 않는다(spec.md FR-003).
- 로그 파일(`.zenuml/log/<slug>.md`)은 절대 덮어쓰지 않고 항상 이어붙인다(spec.md FR-004).
- 로그가 위치하는 디렉토리는 기본적으로 버전관리 대상이 아니어야 한다(spec.md FR-006) — 기존 `.zenuml/` gitignore 규칙을 그대로 재사용한다.
- git은 무시된 디렉토리 안의 파일을 일반 `git add`로 스테이징할 수 없으므로, 선별적 스테이징에는 `git add -f`(force)가 필요하다.
- 이 기능은 `generating-zenuml-diagrams` 스킬 하나에만 적용된다 — 다른 Spec Kit 스킬 파일을 수정해 인용 감지를 자동화하지 않는다(spec.md Assumptions).
- 로그 항목의 자동 요약·패턴 자동 탐지는 만들지 않는다(spec.md FR-008).

**Scale/Scope**: 기존 skill 디렉토리 확장(`SKILL.md` 수정만, 산출물은 feature 001이 이미 만드는 위치를 재사용하고 로그용 하위 디렉토리 하나만 새로 생김). 개인(저장소 소유자) 사용 전제(spec.md Assumptions).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`는 아직 `[PROJECT_NAME]` 등 템플릿 placeholder 상태이며 비준된(ratified) 원칙이 없다 — feature 001의 plan.md와 동일한 상태다. 대조할 공식 게이트가 존재하지 않으므로 이번 계획 단계에서도 Constitution Check를 **적용 불가(N/A)** 로 처리하고 위반 사항 없음으로 진행한다.

**Post-Phase 1 재확인**: Phase 1 설계(data-model.md, contracts/, quickstart.md) 완료 후에도 constitution이 여전히 placeholder 상태임을 재확인함 — 상태 변화 없음, 게이트 여전히 N/A.

## Project Structure

### Documentation (this feature)

```text
specs/002-diagram-feedback-log/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── feedback-interface.md
├── checklists/
│   └── requirements.md  # /speckit-specify output
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
.claude/skills/generating-zenuml-diagrams/
├── SKILL.md              # 기존 워크플로 맨 앞에 "요청 종류 판단" 절을 새로
│                          # 추가(최초 생성 / 재생성 / slug 충돌로 인한 새 요청을
│                          # 가장 먼저 가른다). 그 판단 결과에 따라 기존 "생성 →
│                          # 자기검증 → 출력 파일" 흐름이 분기하고, 재생성/로깅/
│                          # 인용 스테이징 절이 추가된다.
└── references/
    └── syntax.md          # 변경 없음

.zenuml/                   # 기존 gitignore 규칙(.gitignore:10)이 이미 커버
├── <slug>.md               # 기존(feature 001): 다이어그램 산출물.
│                            # 이번 기능에서 재생성마다 전체 교체됨(과거 버전 미보존).
└── log/                    # 신규 하위 디렉토리 — .zenuml/ 안이라 별도 gitignore
    └── <slug>.md            # 항목 불필요. 최초 요청+응답부터 재생성마다
                              # 계속 append되는 이력 파일.
```

**Structure Decision**: 이 기능은 새 skill이 아니라 기존 `generating-zenuml-diagrams` skill의 확장이므로, "Option 1/2/3" 소스 구조가 적용되지 않는다. 실제 변경은 기존 `SKILL.md` 워크플로 맨 앞에 판단 절차를 추가하고 그 아래로 재생성·로깅·인용 스테이징 절을 잇는 것뿐이다. 산출물은 feature 001이 이미 쓰는 `.zenuml/`을 그대로 쓰고, 로그는 그 하위에 새 디렉토리 하나(`.zenuml/log/`)만 생긴다. 별도의 `src/`, `tests/`, 백엔드/프론트엔드 분리는 필요하지 않다(feature 001의 선례와 동일한 구조 결정).

## Complexity Tracking

*No constitution violations to justify — Constitution Check is N/A (no ratified constitution). This section is intentionally empty.*
