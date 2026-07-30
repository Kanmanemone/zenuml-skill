# Implementation Plan: ZenUML Diagram Skill

**Branch**: `001-zenuml-diagram-skill` | **Date**: 2026-07-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-zenuml-diagram-skill/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

자연어로 설명된 프로세스를 입력받아, 명시된 내용만 반영한 정확하고 군더더기 없는 ZenUML 시퀀스 다이어그램 DSL을 생성하는 Claude Code Skill을 만든다. 기술적 접근: 실행 가능한 코드가 아니라 `.claude/skills/<name>/`에 번들링되는 지침·참조 문서 형태로 구현한다 — SKILL.md에 생성/자기검증/명확화/출력-파일 워크플로를 담고, `mermaid-js/zenuml-core`의 `docs/DSL_SYNTAX.md`(MIT)를 재구성한 문법 레퍼런스를 별도 참조 파일로 1단계 깊이에 번들링해 네트워크 접근 없이 동작하도록 한다. 자기검증을 통과한 다이어그램은 채팅 응답에 코드로 노출하지 않고, ZenUML 원문을 Mermaid `zenuml` 코드펜스 형태로 저장소의 `.zenuml/`(gitignore 처리됨) 아래 파일에 저장한 뒤, 그 파일을 가리키는 상대 경로 링크만 응답에 남긴다(FR-011) — Claude Artifact 방식은 발행 시 클라이언트가 자동으로 미리보기를 띄우는 동작을 억제할 수 없어 폐기했고, VS Code 1.121+가 마크다운 프리뷰에서 Mermaid `zenuml` 타입까지 네이티브로 렌더링하는 것을 실측으로 확인해 별도 번역 없이 원문을 그대로 저장하는 로컬 파일 방식을 채택했다(research.md 참조).

## Technical Context

**Language/Version**: N/A — 실행 코드가 없는 Markdown 기반 Skill(지침 + 참조 문서 번들). Claude Code Skill 포맷(YAML frontmatter + Markdown 본문)을 사용한다.

**Primary Dependencies**: 없음 — 외부 라이브러리/런타임 의존성 없이, Claude Code가 파일시스템에서 읽는 정적 Markdown 파일로만 구성된다.

**Storage**: 영속 데이터베이스는 없음. 다만 FR-011에 따라 런타임에 생성되는 다이어그램 출력 파일을 프로젝트 루트의 `.zenuml/`에 저장한다 — 이 디렉터리는 `.gitignore`에 포함되어 있어 버전관리 대상이 아니다(research.md, Decision: 출력 파일 위치와 이름).

**Testing**: 자동화된 테스트 프레임워크 없음(코드가 없으므로). 대신 Anthropic 공식 skill 저작 가이드의 "평가 먼저 만들기(evaluation-driven development)" 권장에 따라, spec.md의 User Story 1~3과 Edge Case를 커버하는 대표 프롬프트 시나리오(최소 3개)를 `quickstart.md`에 정의하고, 수동으로 실행해 성공 기준(SC-001~SC-005) 충족 여부를 검증한다.

**Target Platform**: Claude Code (CLI/IDE) — 이 저장소의 기존 `.claude/skills/*`와 동일한 실행 환경.

**Project Type**: single — 별도 프론트엔드/백엔드 구분이 없는 단일 skill 모듈 추가.

**Performance Goals**: N/A — 런타임 서비스가 아니므로 처리량/응답시간 같은 성능 목표가 적용되지 않는다. 응답 속도는 일반적인 Claude 대화 응답 속도를 따른다.

**Constraints**:
- Claude API 실행 환경은 네트워크 접근이 없으므로, ZenUML 문법 레퍼런스는 반드시 skill 디렉터리 내부에 번들링돼야 한다 (research.md, Data & Constraints).
- Anthropic 공식 가이드 권장에 따라 SKILL.md 본문은 약 500줄 이내로 유지하고, 상세 문법은 별도 참조 파일로 분리해 SKILL.md에서 1단계 깊이로만 링크한다.
- `references/syntax.md`는 `mermaid-js/zenuml-core`의 `docs/DSL_SYNTAX.md`(MIT)를 재구성한 것이므로, 원출처 및 라이선스 고지를 유지해야 한다(spec.md FR-009).
- 출력 파일은 새 렌더러를 구축하지 않고 VS Code가 이미 내장한 Mermaid 렌더링만 사용한다 — 파일 저장이 불가능한 환경에서는 채팅 응답에 ZenUML DSL 텍스트를 직접 제공한다(spec.md FR-011, Edge Cases).
- `.zenuml/`은 생성물 디렉터리이므로 `.gitignore`에 포함되어야 한다(research.md, Decision: 출력 파일 위치와 이름).

**Scale/Scope**: 단일 skill 디렉터리(`SKILL.md` + 참조 파일 1개), 시퀀스 다이어그램 전용, 개인(저장소 소유자) 사용 전제 (spec.md Assumptions).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`는 아직 `[PROJECT_NAME]` 등 템플릿 placeholder 상태이며 비준된(ratified) 원칙이 없다 — 대조할 공식 게이트가 존재하지 않는다. 따라서 이번 계획 단계에서는 Constitution Check를 **적용 불가(N/A)** 로 처리하고 위반 사항 없음으로 진행한다. 추후 constitution이 채워지면 이 계획을 재검토해야 한다.

**Post-Phase 1 재확인**: Phase 1 설계(data-model.md, contracts/, quickstart.md) 완료 후에도 constitution이 여전히 placeholder 상태임을 재확인함 — 상태 변화 없음, 게이트 여전히 N/A.

## Project Structure

### Documentation (this feature)

```text
specs/001-zenuml-diagram-skill/
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
.claude/skills/generating-zenuml-diagrams/
├── SKILL.md              # 워크플로: 생성 → 안티패턴 자기검증 → (필요시) 명확화 질문 → .zenuml/ 출력 파일 링크
└── references/
    └── syntax.md          # ZenUML DSL 문법 레퍼런스 (mermaid-js/zenuml-core docs/DSL_SYNTAX.md 재구성, MIT 출처 고지 포함)
```

**Structure Decision**: 이 기능은 전통적인 애플리케이션이 아니라 Claude Code Skill이므로, "Option 1/2/3" 소스 구조가 적용되지 않는다. 실제 산출물은 이 저장소가 이미 사용 중인 패턴과 동일하게 `.claude/skills/<skill-name>/` 아래에 `SKILL.md` + 참조 파일 1개로 구성되는 단일 skill 모듈이다(research.md, Prior Art — 저장소 내 기존 15개 speckit skill과 동일 패턴). 별도의 `src/`, `tests/`, 백엔드/프론트엔드 분리는 필요하지 않다.

## Complexity Tracking

*No constitution violations to justify — Constitution Check is N/A (no ratified constitution). This section is intentionally empty.*
