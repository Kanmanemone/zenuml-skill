# Implementation Plan: Architecture View Skill

**Branch**: `003-architecture-view-skill` | **Date**: 2026-07-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-architecture-view-skill/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

자연어 프로세스 설명으로부터, 목적(온보딩/특정 문제 진단/기타, 실제로 불분명할 때만 확인)을 판단한 뒤 세 섹션으로 구성된 구조 뷰를 생성하는 Claude Code Skill(`generating-architecture-views`)을 만든다: **Dependency**(컴포넌트·근거 있는 그룹·관계 성격 레이블·색상 구분이 있는 Mermaid `flowchart LR` 다이어그램), **Responsibility**(각 그룹·요소의 책임을 책임(추상)/역할(구체) 두 단계로 서술), **Collaboration**(실제 의존관계가 있는 그룹·요소 쌍에 대해 책임의 경계/분리 이유&합리성 평가/내가 할 수 있는 질문을 담은 항목 — 다수 대상은 조건에 따라 하나의 서술로 통합). 그룹·요소 이름에는 분석 대상 성격에 맞는 하이퍼링크(로컬 상대 경로/웹 URL/링크 없음)가 붙는다. 이 스킬은 구조 뷰만 만드는 독립 스킬이다. 기술적 접근: `.agents/skills/generating-architecture-views/`(`.claude/skills/`는 링크)에 번들링되는 지침 문서와, 규칙만으로 정해지는 일을 맡는 Python 표준 라이브러리 스크립트로 구현하며, 산출물은 `.zenuml/<slug>.architecture.md`에 저장한다.

## Technical Context

**Language/Version**: Markdown 기반 Skill(지침 + 참조 문서 번들, Claude Code Skill 포맷 — YAML frontmatter + Markdown 본문)과, 규칙만으로 정해지는 일을 맡는 Python 3.9+ 스크립트(`scripts/`: 설정 읽기, 다이어그램 고정 부분, hover 패널).

**Primary Dependencies**: 없음(스크립트는 표준 라이브러리만 쓴다). 다른 스킬에도 의존하지 않는 독립 스킬이다(spec.md FR-014).

**Storage**: 영속 데이터베이스는 없음. FR-021에 따라 구조 뷰 출력 파일을 프로젝트 루트의 `.zenuml/`에 저장한다 — 이미 `.gitignore`에 포함된 기존 디렉터리를 그대로 재사용한다.

**Testing**: `build_diagram.build()`를 직접 호출하는 작은 회귀 테스트로 CRUD 표시 없음·각 표시 하나씩·세 표시 전부를 확인하고, `quickstart.md` 시나리오 25에서 Mermaid 미리보기까지 확인한다. 기존 hover 스크립트는 `specs/009-hover-detail-panel/fixtures/`로 확인한다.

**Target Platform**: Claude Code (CLI/IDE) — 이 저장소의 기존 `.claude/skills/*`와 동일한 실행 환경.

**Project Type**: single — 별도 프론트엔드/백엔드 구분이 없는 단일 skill 모듈 추가.

**Performance Goals**: N/A — 런타임 서비스가 아니므로 처리량/응답시간 같은 성능 목표가 적용되지 않는다.

**Constraints**:
- 목적(Purpose)이 실제로 불분명할 때만 확인 질문을 거쳐야 하며, 이미 명시됐거나 추론 가능하면 되묻지 않고 그 목적으로 바로 구조 뷰를 생성해야 한다(spec.md FR-001~003).
- Dependency, Responsibility, Collaboration 세 섹션을 항상 이 순서로 생성해야 한다(FR-005).
- Dependency는 `flowchart LR` + 그룹별 `direction TB` + 코드펜스 맨 앞의 고정 YAML frontmatter `config` 스타일 블록을 쓰고(엣지는 `eN@` ID와 엣지 클래스로 색칠, 라벨이 ID와 다른 노드는 `@{ label }`), 각 화살표에 관계 성격 레이블을, 각 노드·그 노드발 화살표에 일관된 색상을 부여해야 한다(FR-007~008b). 사용자가 요청에서 명시적으로 렌더러(예: "elk")를 지정한 경우에 한해 YAML `config` 바로 아래에 `layout`을 그 값 그대로 추가해야 하며, 명시하지 않은 요청(재생성 포함)에서는 이전 라운드 값을 이어받지 않고 생략해야 한다 — 렌더러 이름은 관계 성격 레이블과 동일하게 열린 어휘이고 검증·매핑 로직을 두지 않는다(FR-007b).
- 요청은 매번 구조(정적)와 구조 변화(동적) 중 하나로 분류하고, 동적이면 설명이 밝힌 노드에만 이모지 라벨과 CRUD 클래스를 붙인다. CRUD class가 하나 이상이면 스크립트가 제목 없는 `✨: 추가<br/>♻️: 변경<br/>🗑️: 삭제` text node를 하나 추가한다(FR-034, FR-035).
- 실제로 확인한 노드의 Dependency 라벨은 007의 `dependency.nodeNameFormat` 세 boolean을 독립적으로 따른다. `declarationMarkers`는 파일 내부 선언의 원본 키워드, `fileExtensions`는 파일 자체 노드의 마지막 확장자, `functionParentheses`는 확인된 함수 이름 끝 `()`만 제어한다. 기본값은 각각 `false`, `false`, `true`다. 확인하지 못했거나 선언도 파일도 아닌 노드는 이름만 두고, 라벨에 부가 설명을 넣지 않으며, 본문의 굵은 이름·노드 ID·링크·hover 내용에는 적용하지 않는다. 스킬이 해석된 세 값을 라벨에 적용하고 `build_diagram.py`와 schema 기반 설정 로더는 바꾸지 않는다(FR-036, 007 FR-012d, research.md "노드 규격 표시어").
- Responsibility는 더 이상 쌍을 비교하지 않는다 — 그룹·요소마다 책임(추상)/역할(구체)을 서술해야 한다(FR-009~010). 다만 같은 그룹·같은 관계 성격에서 병렬적 구조적 역할만 수행하는 요소가 3개 이상이면(종류가 다른 역할을 가진 대상은 제외), 각각 대신 "A, B, C" 이름을 모두 나열한 하나의 통합 항목으로 서술할 수 있다(FR-009b).
- Collaboration은 실제 의존관계가 있는 그룹·요소 쌍에만 항목을 만들고, 각 항목에 책임의 경계/분리 이유&합리성 평가/내가 할 수 있는 질문 세 하위 항목을 담아야 하며, 다수 대상 통합 조건(같은 그룹·같은 관계 성격·3개 이상·병렬적 구조적 역할 — 개별 이름/구현 차이나 개별 엣지가 있어도 무방하며, 종류가 다른 역할을 가진 대상만 제외)을 만족하면 서술적 표현으로 압축해야 한다(FR-025~027b). Responsibility(FR-009b)와 Collaboration(FR-027b)은 동일한 통합 판단 기준을 재사용한다.
- 그룹·요소 이름에는 분석 대상에 맞는 하이퍼링크(로컬 상대 경로/URL/링크 없음)를 붙여야 하며, 로컬 경로 `click`을 쓰더라도 클릭 이동 제약 같은 안내는 덧붙이지 않는다(FR-027c~027d). 산출 파일은 세 섹션의 실제 내용과 Dependency의 요청 키워드 기반 한 줄 캡션만 담고, 메타 코멘트는 넣지 않는다(FR-032, FR-033).
- 근거 없는 컴포넌트·그룹·관계·책임·링크를 지어내서는 안 되고, 근거 없이 그룹/컴포넌트를 세분화해 항목 수를 늘려서도 안 된다(FR-004, FR-006, FR-011, FR-022).
- "헷갈리는 개념 비교" 같은 일반적 개념 비교 섹션은 만들지 않는다 — 비교는 오직 실제 식별된 그룹·요소 간에만(FR-013).
- 구조 뷰만 만든다 — 시퀀스·실행 흐름 다이어그램을 그리거나 다른 스킬의 실행을 제안·질문·실행해서는 안 된다(FR-014, 2026-11-13 개정).
- 출력 파일은 같은 슬러그의 `.zenuml/<slug>.md`와 슬러그를 공유하되 구분되는 별도 파일이어야 한다(FR-021).

**Scale/Scope**: 단일 skill 디렉터리(`SKILL.md` + 참조 파일), 자연어 입력 전용, 개인(저장소 소유자) 사용 전제 (spec.md Assumptions). 섹션이 2개(Components & Dependencies, Responsibility)에서 3개(Dependency, Responsibility, Collaboration)로 늘고, 다이어그램 스타일링·하이퍼링크 결정·다수 대상 통합이라는 세 가지 새 복잡도가 추가되어, appetite는 이전 라운드의 `medium`보다 한 단계 더 높다고 재평가한다 — 다만 목적 확인·위임·피드백 로그 메커니즘은 그대로 재사용되므로 완전한 재설계는 아니다.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

기준: `.specify/memory/constitution.md` v1.1.1(2026-11-15 비준). 이 절을 처음 쓸 때(2026-07-31)는 헌법이 placeholder라 N/A였고, 아래는 2026-11-21 CRUD 이모지 범례 계획에서 다시 점검한 결과다.

| 원칙 | 점검 | 결과 |
|------|------|------|
| I. 오버엔지니어링 금지 | 기존 `build_diagram.py`의 CRUD 수집 결과와 Mermaid 공식 text shape만 재사용한다. 설정·의존성·별도 생성 단계를 추가하지 않는다 | 통과 |
| II. 요청은 해당 Spec에서 진행 | 기존 003의 CRUD 변화 표시 출력 계약을 갱신한다 | 통과 |
| III. 출력 변동성 수정에 Spec Kit 미사용 | 모든 해당 산출물에 적용되는 새 범례 계약이므로 출력 변동성 수정이 아니다 | 해당 없음 |

**Post-Phase 1 재확인**: research.md·data-model.md·contracts·quickstart 반영 뒤에도 새 런타임 의존성·설정·에이전트 판단이 없다. 작은 회귀 테스트 외에는 새 파일도 없다. 위반 없음.

## Project Structure

### Documentation (this feature)

```text
specs/003-architecture-view-skill/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── test_build_diagram.py # CRUD 범례 조건의 작은 회귀 테스트
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── skill-interface.md
├── checklists/
│   └── requirements.md  # /speckit-specify output
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
.agents/skills/generating-architecture-views/   # 원본 (.claude/skills/generating-architecture-views는 이 폴더로의 링크)
├── settings.jsonc / settings.schema.json       # 출력 설정과 그 스키마(007)
├── SKILL.md              # 워크플로: 목적 판단(필요시만 확인) → Dependency 생성(자동 그룹핑, 관계 레이블, 색상) → Responsibility 생성(그룹/요소별 책임(추상)/역할(구체)) → Collaboration 생성(의존관계 있는 쌍만, 3필드, 다수 대상 통합) → 하이퍼링크 결정 → 안티패턴 자기검증 → .zenuml/<slug>.architecture.md 저장 → 파일 링크 제시
├── scripts/
│   ├── read_settings.py  # 설정 읽기·검증(007)
│   ├── build_diagram.py  # 고정 부분과 조건부 CRUD 범례를 채움(FR-008d)
│   ├── apply_hover.py    # hover 패널 적용(009)
│   └── hover/            # hover 스크립트 모듈(009)
└── references/
    ├── templates.md      # Dependency/Responsibility/Collaboration 섹션의 Mermaid/서식 템플릿과 표기 규칙(색상 팔레트, click 규칙 포함)
    └── examples.md       # 완성된 구조 뷰 예시(온보딩·특정 문제 진단 목적, 하이퍼링크 3가지 모드, 다수 대상 통합 포함)
```

함수 라벨 호환성 때문에 기존 이름 정규화 두 곳만 함께 수정한다: `scripts/hover/view_parser.py`와 `.agents/skills/revealing-code-step-by-step/scripts/stages.py`. 새 공용 모듈이나 언어별 함수 키워드 목록은 만들지 않는다.

**Structure Decision**: 이 기능은 전통적인 애플리케이션이 아니라 Claude Code Skill이므로 "Option 1/2/3" 소스 구조가 적용되지 않는다. 실제 산출물은 이 저장소가 이미 사용 중인 `SKILL.md` + `references/` + `scripts/` 패턴으로 구성되는 단일 skill 모듈이다(research.md, Decision: 참조 파일 구조 참고). 별도의 `src/`, `tests/`, 백엔드/프론트엔드 분리는 필요하지 않다.

**다이어그램 고정 부분 스크립트 (FR-008d)**: `scripts/build_diagram.py <.zenuml/<slug>.architecture.md> [--layout=<값>]`. Python 3.9 이상, 표준 라이브러리만(009 hover 스크립트와 같은 실행 방식, 설정은 `scripts/hover/settings.py`로 읽음).
- 입력: `### Dependency` 아래 첫 `mermaid` 펜스. 스킬이 쓴 기본 모양은 `flowchart LR` → 노드·그룹 선언(`subgraph`/`direction TB`/`end` 포함) → `Source -->|관계| Target` 엣지 → (동적이면) `class <Id> crud*` 줄 → `click` 줄이다. 이미 엣지 ID(`eN@`)가 있으면 손대지 않고 0이 아닌 코드로 끝난다.
- 출력: 기존 완성 모양에, 수집한 CRUD class 줄이 하나 이상일 때만 `CrudLegend@{ shape: text, label: "✨: 추가<br/>♻️: 변경<br/>🗑️: 삭제" }`를 CRUD 구역 끝에 추가한다. 그 밖의 출력 순서는 바꾸지 않는다.
- 실행 순서: 산출 파일 쓰기 → `build_diagram.py` → 로그 라운드 쓰기(완성된 파일 내용) → `apply_hover.py`.
- Python이 없거나 0이 아닌 코드로 끝나면 파일은 기본 모양 그대로 두고 응답 끝에 `⚙️ 다이어그램 서식 건너뜀: <이유>` 한 줄을 남긴다.

## Complexity Tracking

*No constitution violations to justify. This section is intentionally empty.*
