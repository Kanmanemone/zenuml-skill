# Implementation Plan: 스킬별 사용자 편집 설정 파일

**Branch**: `007-skill-output-settings` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-skill-output-settings/spec.md`

## Summary

세 스킬(`generating-architecture-views`, `generating-zenuml-diagrams`, `exporting-markdown-diagrams`) 디렉터리에 각각 사용자가 편집하는 `settings.jsonc`(영어 키·값, 한국어 주석)와 그 스킬 옵션의 유일한 기준인 `settings.schema.json`(옵션 정의)을 둔다. 설정 읽기·검증·기본값 대체·안내는 옵션 정의만 보고 동작하는 공통 절차로 만든다 — LLM이 따르는 두 스킬은 SKILL.md의 "Settings" 절 하나로, 스크립트 기반 스킬은 `scripts/lib/settings.js` 하나로. 각 옵션의 실제 동작(섹션 표시 방식, 렌더러, 로그·산출물 위치, 질문 여부와 "(기본값)" 표시, PNG 배율)은 해당 생성·변환 단계에만 더한다. 문서 전체 PDF는 접은 글 상자를 항상 펼쳐 담는다.

## Technical Context

**Language/Version**: Markdown 지침 문서(SKILL.md, references) + Node.js ESM 스크립트(exporting 스킬, 기존과 동일)

**Primary Dependencies**: 새 의존성 없음. exporting 스크립트의 기존 의존성(`@mermaid-js/mermaid-cli`, `markdown-it`, `puppeteer`)만 쓴다. 주석 허용 JSON 파싱은 의존성 없이 직접 구현한다(research.md 참고).

**Storage**: 파일 — 스킬 디렉터리 안의 `settings.jsonc`, `settings.schema.json`

**Testing**: 자동화 테스트 프레임워크 없음(기존 스킬과 동일). exporting 스크립트는 `quickstart.md`의 실행 시나리오로 직접 돌려 확인하고, LLM 스킬은 quickstart 시나리오를 수동 실행해 SC를 확인한다.

**Target Platform**: Claude Code(Windows/macOS/Linux), VS Code 마크다운 미리보기

**Project Type**: Claude Code skill 묶음(지침 문서 + 번들 스크립트)

**Performance Goals**: 설정 읽기로 늘어나는 agent 토큰은 실행당 작은 파일 두 개(설정·옵션 정의) 분량으로 제한한다. `hidden`은 섹션 생성 자체를 건너뛰어 토큰을 줄인다.

**Constraints**: 기본값(잠정)은 기능 도입 전 동작과 같아야 한다(FR-003). 변환 결과는 LLM 판단에 의존하지 않는다(004 원칙, FR-015b). 각 스킬은 다른 스킬을 전제하지 않는 독립 스킬이다(003 FR-014) — 공통 절차도 스킬마다 자기 안에 둔다.

**Scale/Scope**: 옵션 10개(architecture 3, zenuml 1, exporting 6 — `questions.enabled`, `defaults.format/scope/pdfLayout`, `png.scale`, `output.directory`)와 고정 동작 1개(PDF 펼침).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`가 템플릿 placeholder 상태 — 비준된 원칙이 없으므로 게이트 **N/A**, 위반 없음. Phase 1 설계 후 재확인: 변화 없음.

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
.claude/skills/generating-architecture-views/
├── SKILL.md                 # "Settings" 절(공통 절차) + 표시 방식·렌더러 동작 규칙
├── settings.jsonc           # 신규 — 사용자 편집용, 한국어 주석
├── settings.schema.json     # 신규 — 옵션 정의(유일한 기준)
└── references/templates.md  # 접은 글 상자 형식 추가

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
