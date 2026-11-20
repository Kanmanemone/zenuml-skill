# Implementation Plan: 스킬별 사용자 편집 설정 파일

**Branch**: `007-skill-output-settings` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-skill-output-settings/spec.md`

## Summary

세 스킬(`generating-architecture-views`, `generating-zenuml-diagrams`, `exporting-markdown-diagrams`) 디렉터리에 각각 사용자가 편집하는 `settings.jsonc`(영어 키·값, 한국어 주석)와 그 스킬 옵션의 유일한 기준인 `settings.schema.json`(옵션 정의)을 둔다. 설정 읽기·검증·기본값 대체·안내는 옵션 정의만 보고 동작하는 공통 절차로 만든다 — LLM이 따르는 두 스킬은 SKILL.md의 "Settings" 절 하나로, 스크립트 기반 스킬은 `scripts/lib/settings.js` 하나로. 각 옵션의 실제 동작(섹션 표시 방식, 렌더러, 노드 표시어·함수 괄호, 로그·산출물 위치, 질문 여부와 "(기본값)" 표시, PNG 배율)은 해당 생성·변환 단계에만 더한다. 문서 전체 PDF는 접은 글 상자를 항상 펼쳐 담는다.

## Technical Context

**Language/Version**: Markdown 지침 문서(SKILL.md, references) + Python 3.9+ 설정 로더(generating 스킬) + Node.js ESM 스크립트(exporting 스킬, 기존과 동일)

**Primary Dependencies**: 새 의존성 없음. exporting 스크립트의 기존 의존성(`@mermaid-js/mermaid-cli`, `markdown-it`, `puppeteer`)만 쓴다. 주석 허용 JSON 파싱은 의존성 없이 직접 구현한다(research.md 참고).

**Storage**: 파일 — 스킬 디렉터리 안의 `settings.jsonc`, `settings.schema.json`

**Testing**: 기존 설정 로더 테스트와 `quickstart.md`의 실행 시나리오를 쓴다. 새 boolean 기본값은 `read_settings.py` 출력으로 자동 확인하고, 네 가지 노드 이름 조합은 지침과 생성 결과를 대조한다.

**Target Platform**: Claude Code(Windows/macOS/Linux), VS Code 마크다운 미리보기

**Project Type**: Claude Code skill 묶음(지침 문서 + 번들 스크립트)

**Performance Goals**: 설정 읽기로 늘어나는 agent 토큰은 실행당 작은 파일 두 개(설정·옵션 정의) 분량으로 제한한다. `hidden`은 섹션 생성 자체를 건너뛰어 토큰을 줄인다.

**Constraints**: 기본값은 기능 도입 전 동작과 같아야 하되, 사용자가 명시적으로 정한 노드 이름 기본값은 예외다(FR-003, FR-012d). 변환 결과는 LLM 판단에 의존하지 않는다(004 원칙, FR-015b). 각 스킬은 다른 스킬을 전제하지 않는 독립 스킬이다(003 FR-014) — 공통 절차도 스킬마다 자기 안에 둔다.

**Scale/Scope**: 기존 옵션에 architecture boolean 2개(`dependency.nodeMarkers`, `dependency.functionParentheses`)를 추가하고, 고정 동작 1개(PDF 펼침)는 유지한다.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

기준: `.specify/memory/constitution.md` v1.1.1(2026-11-15 비준).

| 원칙 | 점검 | 결과 |
|------|------|------|
| I. 오버엔지니어링 금지 | 기존 schema 기반 boolean 로더를 재사용하고 새 스크립트·키워드 목록·추상화를 만들지 않는다 | 통과 |
| II. 요청은 해당 Spec에서 진행 | 설정 계약은 007, 노드 라벨 출력 계약은 기존 003에서 갱신한다 | 통과 |
| III. 출력 변동성 수정에 Spec Kit 미사용 | 사용자가 제어하는 영속 설정과 기본값을 추가하는 요구사항 변화다 | 해당 없음 |

**Post-Phase 1 재확인**: 새 옵션 두 개와 기존 라벨 규칙의 조건화만 설계했으며 새 의존성이나 실행 계층은 없다. 위반 없음.

## Project Structure

### Documentation (this feature)

```text
specs/007-skill-output-settings/
├── plan.md              # 이 파일
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── settings-contract.md   # 설정 파일·옵션 정의 형식과 공통 처리 규약
└── tasks.md             # /speckit-tasks 산출물
```

### Source Code (repository root)

```text
.agents/skills/generating-architecture-views/
├── SKILL.md                 # 설정 절 + 표시 방식·렌더러·노드 이름 규칙
├── settings.jsonc           # 사용자 편집용, 한국어 주석
├── settings.schema.json     # 옵션 정의(유일한 기준)
├── scripts/read_settings.py # 기존 schema 기반 설정 해석기
└── references/templates.md  # 접은 글 상자·노드 이름 형식

.claude/skills/generating-zenuml-diagrams/
├── SKILL.md                 # "Settings" 절 + 로그 위치 규칙
├── settings.jsonc           # 신규
└── settings.schema.json     # 신규

.claude/skills/exporting-markdown-diagrams/
├── SKILL.md                 # 설정 읽기 단계 + 질문 여부·"(기본값)" 표시 규칙
├── settings.jsonc           # 신규
├── settings.schema.json     # 신규
└── scripts/
    ├── read-settings.js     # 신규 — 해석된 설정과 안내 문구를 JSON으로 출력
    ├── export-diagrams.js   # png.scale, output.directory 적용
    ├── export-document-pdf.js  # output.directory 적용, 접은 글 상자 펼침
    └── lib/
        ├── settings.js      # 신규 — 옵션 정의 기반 공통 로더(JSONC 파싱·검증·안내)
        └── export-dir.js    # output.directory를 받도록 변경
```

**Structure Decision**: 옵션 정의를 사람이 읽는 표가 아니라 기계가 읽는 `settings.schema.json`으로 둔다. 그래야 스크립트 로더와 LLM 절차가 같은 기준을 보고, 옵션 추가가 정의 한 항목 + 동작 규칙 + 설정 파일 한 줄(FR-018)로 끝난다.

## Complexity Tracking

해당 없음.
