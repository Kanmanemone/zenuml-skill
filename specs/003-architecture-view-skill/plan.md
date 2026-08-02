# Implementation Plan: Architecture View Skill

**Branch**: `003-architecture-view-skill` | **Date**: 2026-07-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-architecture-view-skill/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

자연어 프로세스 설명으로부터, 목적(온보딩/특정 문제 진단/기타, 실제로 불분명할 때만 확인)을 판단한 뒤 세 섹션으로 구성된 구조 뷰를 생성하는 Claude Code Skill(`generating-architecture-views`)을 만든다: **Dependency**(컴포넌트·근거 있는 그룹·관계 성격 레이블·색상 구분이 있는 Mermaid `flowchart LR` 다이어그램), **Responsibility**(각 그룹·요소의 책임을 책임(추상)/역할(구체) 두 단계로 서술), **Collaboration**(실제 의존관계가 있는 그룹·요소 쌍에 대해 책임의 경계/분리 이유&합리성 평가/내가 할 수 있는 질문을 담은 항목 — 다수 대상은 조건에 따라 하나의 서술로 통합). 그룹·요소 이름에는 분석 대상 성격에 맞는 하이퍼링크(로컬 상대 경로/웹 URL/링크 없음)가 붙는다. 이 스킬은 `generating-zenuml-diagrams`에 의존한다 — 구조 뷰가 완성되면 시퀀스 다이어그램까지 만들지 사용자에게 확인하고, 동의할 때만 구조 뷰 내용을 컨텍스트로 담아 그 스킬을 실행한다. 기술적 접근: 실행 코드가 아니라 `.claude/skills/generating-architecture-views/`에 번들링되는 지침 문서로 구현하며, 산출물은 같은 프로세스의 `.zenuml/<slug>.md`(시퀀스 다이어그램, 존재한다면)와 슬러그를 공유하는 별도 파일에 저장한다.

## Technical Context

**Language/Version**: N/A — 실행 코드가 없는 Markdown 기반 Skill(지침 + 참조 문서 번들). Claude Code Skill 포맷(YAML frontmatter + Markdown 본문)을 사용한다.

**Primary Dependencies**: 없음(외부 라이브러리/런타임 의존성 없음). 다만 기능적으로 `generating-zenuml-diagrams`(이 저장소의 다른 스킬)에 의존한다 — 구조 뷰 완성 후 사용자가 동의하면 그 스킬을 실행한다(spec.md FR-014~018).

**Storage**: 영속 데이터베이스는 없음. FR-021에 따라 구조 뷰 출력 파일을 프로젝트 루트의 `.zenuml/`에 저장한다 — 이미 `.gitignore`에 포함된 기존 디렉터리를 그대로 재사용한다.

**Testing**: 자동화된 테스트 프레임워크 없음(코드가 없으므로). `generating-zenuml-diagrams`와 동일하게, spec.md의 User Story 1~4와 Edge Case를 커버하는 대표 프롬프트 시나리오를 `quickstart.md`에 정의하고 수동으로 실행해 성공 기준(SC-001~SC-011) 충족 여부를 검증한다.

**Target Platform**: Claude Code (CLI/IDE) — 이 저장소의 기존 `.claude/skills/*`와 동일한 실행 환경.

**Project Type**: single — 별도 프론트엔드/백엔드 구분이 없는 단일 skill 모듈 추가.

**Performance Goals**: N/A — 런타임 서비스가 아니므로 처리량/응답시간 같은 성능 목표가 적용되지 않는다.

**Constraints**:
- 목적(Purpose)이 실제로 불분명할 때만 확인 질문을 거쳐야 하며, 이미 명시됐거나 추론 가능하면 되묻지 않고 그 목적으로 바로 구조 뷰를 생성해야 한다(spec.md FR-001~003).
- Dependency, Responsibility, Collaboration 세 섹션을 항상 이 순서로 생성해야 한다(FR-005).
- Dependency는 `flowchart LR` + 그룹별 `direction TB` + 고정 `%%{init}%%` 스타일 블록을 쓰고, 각 화살표에 관계 성격 레이블을, 각 노드·그 노드발 화살표에 일관된 색상을 부여해야 한다(FR-007~008b).
- Responsibility는 더 이상 쌍을 비교하지 않는다 — 그룹·요소마다 책임(추상)/역할(구체)을 서술해야 한다(FR-009~010). 다만 같은 그룹·같은 관계 성격에서 병렬적 구조적 역할만 수행하는 요소가 3개 이상이면(종류가 다른 역할을 가진 대상은 제외), 각각 대신 "A, B, C" 이름을 모두 나열한 하나의 통합 항목으로 서술할 수 있다(FR-009b).
- Collaboration은 실제 의존관계가 있는 그룹·요소 쌍에만 항목을 만들고, 각 항목에 책임의 경계/분리 이유&합리성 평가/내가 할 수 있는 질문 세 하위 항목을 담아야 하며, 다수 대상 통합 조건(같은 그룹·같은 관계 성격·3개 이상·병렬적 구조적 역할 — 개별 이름/구현 차이나 개별 엣지가 있어도 무방하며, 종류가 다른 역할을 가진 대상만 제외)을 만족하면 서술적 표현으로 압축해야 한다(FR-025~027b). Responsibility(FR-009b)와 Collaboration(FR-027b)은 동일한 통합 판단 기준을 재사용한다.
- 그룹·요소 이름에는 분석 대상에 맞는 하이퍼링크(로컬 상대 경로/URL/링크 없음)를 붙여야 하며, 로컬 경로 `click`을 쓴 경우 VS Code 클릭 이동 제약 안내를 덧붙여야 한다(FR-027c~027d).
- 근거 없는 컴포넌트·그룹·관계·책임·링크를 지어내서는 안 되고, 근거 없이 그룹/컴포넌트를 세분화해 항목 수를 늘려서도 안 된다(FR-004, FR-006, FR-011, FR-022).
- "헷갈리는 개념 비교" 같은 일반적 개념 비교 섹션은 만들지 않는다 — 비교는 오직 실제 식별된 그룹·요소 간에만(FR-013).
- 시퀀스 다이어그램(Runtime Flow)은 직접 그리지 않고, 구조 뷰 완성 후 사용자 동의를 받아 `generating-zenuml-diagrams`를 실행해야 한다 — 동의 없이 자동 실행해서는 안 된다(FR-014~017).
- `generating-zenuml-diagrams`의 SKILL.md나 동작을 수정해서는 안 된다(FR-018).
- 출력 파일은 같은 슬러그의 `.zenuml/<slug>.md`와 슬러그를 공유하되 구분되는 별도 파일이어야 한다(FR-021).

**Scale/Scope**: 단일 skill 디렉터리(`SKILL.md` + 참조 파일), 자연어 입력 전용, 개인(저장소 소유자) 사용 전제 (spec.md Assumptions). 섹션이 2개(Components & Dependencies, Responsibility)에서 3개(Dependency, Responsibility, Collaboration)로 늘고, 다이어그램 스타일링·하이퍼링크 결정·다수 대상 통합이라는 세 가지 새 복잡도가 추가되어, appetite는 이전 라운드의 `medium`보다 한 단계 더 높다고 재평가한다 — 다만 목적 확인·위임·피드백 로그 메커니즘은 그대로 재사용되므로 완전한 재설계는 아니다.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`는 아직 `[PROJECT_NAME]` 등 템플릿 placeholder 상태이며 비준된(ratified) 원칙이 없다 — 대조할 공식 게이트가 존재하지 않는다. 따라서 이번 계획 단계에서는 Constitution Check를 **적용 불가(N/A)** 로 처리하고 위반 사항 없음으로 진행한다.

**Post-Phase 1 재확인**: Phase 1 설계(data-model.md, contracts/, quickstart.md) 완료 후에도 constitution이 여전히 placeholder 상태임을 재확인함 — 상태 변화 없음, 게이트 여전히 N/A.

## Project Structure

### Documentation (this feature)

```text
specs/003-architecture-view-skill/
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
.claude/skills/generating-architecture-views/
├── SKILL.md              # 워크플로: 목적 판단(필요시만 확인) → Dependency 생성(자동 그룹핑, 관계 레이블, 색상) → Responsibility 생성(그룹/요소별 책임(추상)/역할(구체)) → Collaboration 생성(의존관계 있는 쌍만, 3필드, 다수 대상 통합) → 하이퍼링크 결정 → 안티패턴 자기검증 → .zenuml/<slug>.architecture.md 저장 → 시퀀스 다이어그램까지 만들지 확인 → (동의 시) generating-zenuml-diagrams 실행
└── references/
    ├── templates.md      # Dependency/Responsibility/Collaboration 섹션의 Mermaid/서식 템플릿과 표기 규칙(색상 팔레트, click 규칙 포함)
    └── examples.md       # 완성된 구조 뷰 예시(온보딩·특정 문제 진단 목적, 하이퍼링크 3가지 모드, 다수 대상 통합, 위임 동의/거부 각각 포함)
```

**Structure Decision**: 이 기능은 전통적인 애플리케이션이 아니라 Claude Code Skill이므로 "Option 1/2/3" 소스 구조가 적용되지 않는다. 실제 산출물은 이 저장소가 이미 사용 중인 `SKILL.md` + `references/` 패턴과 동일하게 구성되는 단일 skill 모듈이다(research.md, Decision: 참조 파일 구조 참고). 별도의 `src/`, `tests/`, 백엔드/프론트엔드 분리는 필요하지 않다.

## Complexity Tracking

*No constitution violations to justify — Constitution Check is N/A (no ratified constitution). This section is intentionally empty.*
