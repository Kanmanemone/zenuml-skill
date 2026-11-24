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

## 2026-11-21 토큰 효율 보완 계획

`SKILL.md`의 트리거 설명과 중복 예시를 줄인다. 문법 reference와 근거 제한,
자기검증, 출력 계약은 정확성 경계이므로 유지한다. 새 스크립트나 의존성은
추가하지 않으며 피드백 로그 자동화는 002에서 다룬다.

## 2026-11-23 읽기 쉬운 시퀀스 다이어그램 계획 (FR-012, FR-015, FR-016, 007 FR-015d)

- `SKILL.md` "Generation rules": FR-015 작성 규칙 bullet(상태 변경은 호출 위 주석, 상태만 바꾸는 조건 가지는 블록 위 `// → 결과`와 빈 블록, 라벨은 함수와 인자, 자기 메시지는 실제 자기 호출만). "Self-check"의 출력 파일 항목과 "Output and logging"에 `apply_style.py` 실행(저장 직후, 로그 전)을 넣는다.
- `references/syntax.md` "Comments & styling": 빈 블록 안 주석은 그려지지 않는다는 사실 한 줄.
- `scripts/apply_style.py`(새 파일, 표준 라이브러리): `apply_style.py <output> [--style=readable|zenuml-default]`. 같은 폴더의 `read_settings.load_settings`로 `diagram.style`을 읽고, 명령줄 값이 허용되면 우선한다(아니면 `⚙️ 설정 안내`). 파일에서 기존 `<details class="zenuml-style">…</details>`를 지우고, `readable`이면 고정 블록을 끝에 붙인다. 다이어그램 코드펜스는 건드리지 않는다. 블록 CSS는 research "스타일 블록"의 값.
- `settings.schema.json`·`settings.jsonc`: enum `diagram.style`(`readable`, `zenuml-default`, tokenImpact `[0]`)과 한국어 주석.
- 테스트: `specs/001-zenuml-diagram-skill/test_apply_style.py`(블록 추가·교체·제거, 코드펜스 불변, 배포 설정과 schema 기본값 일치).
- 007 문서: data-model 옵션 표와 settings-contract에 `diagram.style`.

**Constitution Check (2026-11-23)**: I — 새 파일은 스크립트 하나와 테스트 하나. 블록은 고정 문자열이고 분기는 두 값뿐이다. 스크립트로 둔 이유는 규칙만으로 정해지는 출력을 모델이 매번 쓰지 않게 하기 위함이다(토큰·변동성). II — 001·007 개정. III — 요구사항 변경. IV — 기본값은 schema와 배포 설정에만, 테스트는 schema와 비교. 위반 없음.

## 2026-11-24 주석 왼쪽 여백 계획 (FR-016)

- `scripts/apply_style.py`의 `BLOCK`에서 `.comment-text` 규칙에 조건식과 같은 `transform: translateX(6px)`를 더한다. ZenUML은 주석을 다음 문장의 x에 그대로 그리므로 조건 블록 밖 주석도 같이 6px 옮겨지지만, 주석이 놓이는 자리에서 6px는 겹침을 만들지 않는다. 블록 밖만 남기는 선택자는 ZenUML SVG에 주석이 블록 안인지 밝히는 표시가 없어 쓸 수 없다.
- research.md의 스타일 블록을 같게 맞춘다. 테스트는 `BLOCK`과 비교하므로 바꿀 것이 없다.

**Constitution Check (2026-11-24 주석 여백)**: I~IV 모두 해당 없음(CSS 선언 하나). 위반 없음.

## Complexity Tracking

*No constitution violations to justify — Constitution Check is N/A (no ratified constitution). This section is intentionally empty.*
