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
- 실제로 확인한 노드의 Dependency 라벨은 007의 `dependency.nodeNameFormat` 세 boolean을 독립적으로 따른다. `declarationMarkers`는 파일 내부 선언의 원본 키워드, `fileExtensions`는 파일 자체 노드의 마지막 확장자, `functionParentheses`는 확인된 함수 이름 끝 `()`만 제어한다. 확인하지 못했거나 선언도 파일도 아닌 노드는 이름만 두고, 라벨에 부가 설명을 넣지 않으며, 본문의 굵은 이름·노드 ID·링크·hover 내용에는 적용하지 않는다. 스킬은 `declarationMarkers`·`functionParentheses`를 라벨에 적용하고 파일 자체 노드에는 항상 확장자를 쓴다. `build_diagram.py`가 `click` 대상에서 파일 이름을 얻어 `fileExtensions=false`의 확장자 제거를 하고 FR-037 표시 대상 노드에 표식 class `srcFile`을 붙인다. 파일 이름 자체는 `apply_hover.py`가 문서 끝 `<details>` 속 `<style>`에 노드별 `::before` 규칙으로 그린다(research.md "파일 이름 표시"), schema 기반 설정 로더는 바꾸지 않는다(FR-036, FR-037, 007 FR-012d, FR-012e, research.md "노드 규격 표시어").
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

기준: `.specify/memory/constitution.md` v1.2.0. 이 절을 처음 쓸 때(2026-07-31)는 헌법이 placeholder라 N/A였고, 아래는 2026-11-21 CRUD 이모지 범례 계획에서 다시 점검한 결과다.

**2026-11-22 파일 이름 표시 이동(FR-037) 점검**: I — 새 스크립트·설정·의존성 없이 기존 `build_diagram.py`의 판정과 `apply_hover.py`의 style 블록을 재사용하고, 라벨 span과 두 `clean_name`의 span 제거를 지운다. II — 기존 003 FR-037을 개정한다. III — 모든 산출물에 적용되는 출력 계약 변경이다. IV — 기본값을 문서에 옮겨 적지 않는다. 위반 없음. 같은 날 테두리 선 위·세 위치 개정도 `style_blocks.py`의 상수와 `apply_hover.py`의 기존 색상 class 해석만 바꾸고 새 파일·의존성이 없어 위반 없음.

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

**다이어그램 고정 부분 스크립트 (FR-008d)**: `scripts/build_diagram.py <.zenuml/<slug>.architecture.md> [--layout=<값>] [--source-file=<true|false>] [--source-file-position=<left|right>] [--file-extensions=<true|false>]`. `--layout` 외의 옵션은 요청이 직접 밝힌 값만 넘긴다(007 FR-006). Python 3.9 이상, 표준 라이브러리만(009 hover 스크립트와 같은 실행 방식, 설정은 `scripts/hover/settings.py`로 읽음).
- 입력: `### Dependency` 아래 첫 `mermaid` 펜스. 스킬이 쓴 기본 모양은 `flowchart LR` → 노드·그룹 선언(`subgraph`/`direction TB`/`end` 포함) → `Source -->|관계| Target` 엣지 → (동적이면) `class <Id> crud*` 줄 → `click` 줄이다. 이미 엣지 ID(`eN@`)가 있으면 손대지 않고 0이 아닌 코드로 끝난다.
- 출력: 기존 완성 모양에, 수집한 CRUD class 줄이 하나 이상일 때만 `CrudLegend@{ shape: text, label: "✨: 추가<br/>♻️: 변경<br/>🗑️: 삭제" }`를 CRUD 구역 끝에 추가한다. 그 밖의 출력 순서는 바꾸지 않는다.
- 실행 순서: 산출 파일 쓰기 → `build_diagram.py` → 로그 라운드 쓰기(완성된 파일 내용) → `apply_hover.py`.
- Python이 없거나 0이 아닌 코드로 끝나면 파일은 기본 모양 그대로 두고 응답 끝에 `⚙️ 다이어그램 서식 건너뜀: <이유>` 한 줄을 남긴다.

## 2026-11-21 토큰 효율 보완 계획

- `scripts/append_feedback.py`: 산출물·요청 요약을 기존 로그 형식으로 복사하는
  표준 라이브러리 helper. 002의 독립 복사본과 같은 계약을 쓴다.
- `references/feedback-log.md`: helper 실패 또는 로그 인용 때만 읽는 수동 형식과
  보존 규칙.
- `SKILL.md`: 전체 완성 예시를 제거하고 기존 examples/templates reference로
  연결한다. 구조 판단 규칙은 본문에 남겨 매번 필요한 판단을 숨기지 않는다.
- `docs/skill-benchmark/run.py`: 네 스킬을 같은 방식으로 비교하고 실제
  input/output token과 턴 수를 기록한다.

## 2026-11-23 점검 반영 계획 (FR-027, FR-040, FR-041)

지침 문서만 고친다. 스크립트·설정·테스트 동작은 바뀌지 않는다.

- `SKILL.md` "Evidence and links": FR-040 판단 규칙을 짧은 bullet로 더하는 유일한 자리다.
  코드 확인 경계(사용자가 준 코드는 읽고, 링크를 찾으려고 그 밖을 탐색하지 않음)를 한 문장으로 합친다.
- `SKILL.md` "Classification"·"Scripts and settings"·"Saving": 목적의 역할, slug 형식,
  `⚙️` 줄만 옮기는 규칙, `log.directory` 기준, 로그 요청 문구를 각 절에 한 줄씩 넣는다.
  설정 파일을 직접 읽지 않는 이유(스크립트가 기본값 병합과 검증을 함)를 붙이고,
  Python이 없을 때 schema `default`만 읽는 예외로 정리한다.
- `SKILL.md` frontmatter `description`: FR-041의 네 요소를 넣고 다른 스킬 이름은 쓰지 않는다.
- `references/templates.md`: 노드 이름 형식·링크 결정 규칙은 `SKILL.md` 참조로 줄이고 모양 규칙만 남긴다.
  Responsibility 통합 조건은 "Multi-target consolidation" 참조로 줄인다. Collaboration의 긴 단락을
  bullet로 나누고 FR-027의 미지 문구 예외를 넣는다. 이력 문구("earlier drafts")를 지운다.
- `references/examples.md`: 첫 예시를 파일 노드 확장자 라벨과 `data` 그룹 분리로 고치고,
  FR-040의 흔한 경우(호출자 없는 문장, 외부 시스템, 중첩 그룹)를 보여 주는 예시 하나를 더한다.
- `references/feedback-log.md`: 바꾸지 않는다(이미 "lightly edited"가 기준).
- `quickstart.md`: SC-018 재실행 시나리오를 더한다.

하지 않는 것: 점검 보고가 제안한 `lint_view.py`, 스킬 폴더 `evals/`, description 트리거 최적화 루프는
이번 요구사항에 없으므로 만들지 않는다(원칙 I). Out of scope 안내에 다른 스킬을 추천하지 않는 것은
FR-014·SC-008이 정한 의도이므로 유지한다.

**Constitution Check (2026-11-23)**: I — 새 파일·스크립트·설정 없이 지침 문장만 고치고 중복을 줄인다. II — 기존 003을 개정한다.
III — 판단이 갈린 경우를 규칙으로 정하는 요구사항 변경이며 단발 출력 차이 수정이 아니다. IV — 기본값을 문서에 옮겨 적지 않는다. 위반 없음.

## 2026-11-23 사용 외 의존 옅은 선 계획 (FR-042~045, SC-019·020, 007 FR-012f·SC-011)

에이전트는 라벨만 고르고, 나머지는 `build_diagram.py`가 라벨로 정한다(research "옅은 선").

- `scripts/build_diagram.py`:
  - `FAINT_LABELS = {"생성", "전달", "타입 참조"}`. `label.strip()`이 이 중 하나와 정확히 같고 설정이 켜져 있으면 그 간선은 옅다.
  - 간선 ID는 지금처럼 원래 순서 `eN`을 그대로 쓰고, `%% ---- 엣지 ----` 아래에는 옅은 간선 줄을 먼저, 진한 간선 줄을 나중에 쓴다(각 무리 안에서는 원래 순서). 켜고 끈 두 산출물의 ID가 같다(SC-011).
  - 엣지 스타일: 진한 간선은 지금의 `<base>Edge`. 옅은 간선이 있는 출발 노드에는 `classDef <base>Faint stroke:<색>4D,stroke-width:3px,color:<색>80`을 `<base>Edge` 바로 다음에 두고 `class eN <base>Faint`로 단다.
  - 범례: 옅은 간선이 하나라도 있으면 `옅은 선: 사용 외 의존 (생성·전달)`을 CRUD 범례 label 끝에 `<br/>`로 붙이고, CRUD가 없으면 같은 `CrudLegend@{ shape: text, … }` 노드를 이 한 줄로 만든다. 이때만 config `flowchart:`에 `wrappingWidth: 400`을 더한다(줄바꿈 방지).
  - 옅은 간선이 없거나 설정이 꺼져 있으면 출력은 지금과 바이트 단위로 같다.
  - 명령줄 `--faint-edges=true|false`: 요청 문장이 값을 밝힐 때만. 기존 `--file-extensions`와 같은 처리로 검증한다(두 옵션의 처리를 표 하나로 합침).
- `settings.schema.json`: boolean `dependency.faintNonUsageEdges`(tokenImpact 두 값 `[0]`). `settings.jsonc`: `dependency` 아래 같은 키와 한국어 주석. 기본값은 schema `default`에만(헌법 IV).
- `SKILL.md` "Evidence and links": 간선 판단을 순서 있는 질문 네 개로 쓴 bullet 하나(① 변경 영향이 없으면 간선 없음 ② 멤버를 쓰면 사용 ③ 이름만 나오면 세 라벨 ④ 이름 없이 동작에 기대면 근거가 밝힐 때만 사용 의존, 라벨에 가정)와 애매할 때의 원칙(사용 쪽, 코드에 숨은 관계일수록 다이어그램이 필요). 기존 "Edge labels use the description's own wording" bullet은 그대로 둔다. "Saving"의 `--faint-edges` 한 구절. 스크립트가 옅게 칠하므로 모양은 쓰지 않는다.
- `references/templates.md` "Dependency template": 스크립트가 채우는 목록에 옅은 선과 범례 줄을 더한다.
- `specs/003-architecture-view-skill/test_build_diagram.py`: 옅은 간선 순서·ID·classDef·범례(CRUD 유무)·`wrappingWidth`, `생성·호출`은 진한 선, 설정 끔과 옅은 간선 없음은 지금 출력과 같음, schema 기본값과 배포 설정이 같음.
- `quickstart.md`: 시나리오 29(SC-019·SC-011, VS Code·GitHub 육안 확인).
- 바뀌지 않는 것: `hover/view_parser.py`(간선 정규식이 순서·class와 무관), `apply_hover.py`, 단계별 코드 공개(010), 기존 산출물(다시 만들 때만 반영).

**Constitution Check (2026-11-23)**: I — 새 파일·의존성 없이 기존 스크립트에 라벨 집합 하나와 조건 분기만 더한다. 설정은 007 FR-012f가 요구한 하나뿐이다. II — 기존 003·007을 개정한다. III — 요구사항 변경이다. IV — 기본값은 schema `default`와 배포 `settings.jsonc`에만 두고, 테스트는 schema와 비교한다. 위반 없음.

## 2026-11-24 링크 노드 글자색 계획 (FR-046, SC-021, 007 FR-012g·SC-012)

에이전트가 쓰는 다이어그램은 바뀌지 않고, `build_diagram.py`가 설정으로 config의 `themeCSS`에 규칙 하나를 더하거나 뺀다(research "링크 노드 글자색").

- `scripts/build_diagram.py`:
  - `LINK_STYLE = "dependency.linkStyle"`를 두고 `FLAGS`에 `"--link-style=": LINK_STYLE`를 더한다. 값 검증은 기존 표 처리(`is_valid`)를 그대로 쓴다.
  - `build(..., link_style="link")`: `"plain"`이면 `themeCSS` 문자열 끝(닫는 `"` 앞)에 ` .node a, .node a:hover { color: inherit !important; text-decoration: none !important; }`를 붙인다. `"link"`면 출력이 지금과 바이트 단위로 같다. 함수 인자 기본값 `"link"`는 "규칙 없음"이라는 뜻이며 설정 기본값이 아니다. `main`은 설정 값을 넘긴다.
- `settings.schema.json`: enum `dependency.linkStyle`(`plain`·`link`, tokenImpact 두 값 `[0]`). `settings.jsonc`: `faintNonUsageEdges` 다음에 같은 키와 한국어 주석. 기본값은 schema `default`에만 둔다(헌법 IV).
- `SKILL.md` "Saving" 2단계: 요청이 값을 밝힐 때만 붙이는 명령줄 목록에 `--link-style=<plain|link>`를 더한다.
- `test_build_diagram.py`: `plain`이면 규칙이 config에 한 번 있고, `link`면 지금 출력과 같으며, 두 출력에서 config 줄 밖이 같은지 본다. 명령줄 값 검증은 기존 테스트 방식으로 본다.
- `quickstart.md`: 시나리오 30(SC-021, VS Code 미리보기 육안 확인).
- 바뀌지 않는 것: `hover/`(config 줄을 읽지 않음), `apply_hover.py`, 단계별 코드 공개(010), 기존 산출물(다시 만들 때만 반영).

**Constitution Check (2026-11-24)**: I — 새 파일·의존성 없이 기존 config 문자열에 조건부 규칙 하나와 명령줄 표 한 줄을 더한다. II — 003·007을 개정한다. III — 새 요구사항이다. IV — 기본값은 schema에만 둔다. 위반 없음. 설계 뒤 다시 확인했고 달라진 것이 없다.

## Complexity Tracking

*No constitution violations to justify. This section is intentionally empty.*
