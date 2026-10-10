# Implementation Plan: 다이어그램 가장자리 잘림 수정

**Branch**: `005-fix-diagram-clipping` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-fix-diagram-clipping/spec.md`

## Summary

zenuml-core 같은 렌더러가 루트 `<svg>`의 `viewBox`를 실제 그림보다 좁게 계산해 export 산출물 가장자리가 잘린다. 모든 다이어그램을 먼저 mmdc로 **SVG로만** 렌더링한 뒤, headless 브라우저에서 루트 `<svg>`의 `getBBox()`로 실제 그림 범위를 재서 넘친 쪽만 `viewBox`를 넓힌다(새 공용 모듈 `scripts/lib/fit-svg.js`). 다이어그램 단독 PNG/PDF는 더 이상 mmdc의 png/pdf 출력을 쓰지 않고, 보정된 SVG를 같은 브라우저로 screenshot/print해서 만든다. 문서 전체 PDF는 mmdc가 추출한 SVG들을 인라인하기 전에 같은 보정을 거친다. 설계의 출발점은 handoff 문서지만, 원인·동작을 독자적으로 재현·측정해 검증했고 그 과정에서 발견한 사실(아래 research.md)을 반영했다.

## Technical Context

**Language/Version**: Node.js (ESM), 실행 확인 v24.19.0

**Primary Dependencies**: `@mermaid-js/mermaid-cli` ^11(설치 11.16.0), `puppeteer` ^25(설치 25.8.0, 이미 직접 의존성), `markdown-it` ^14 — 새 의존성 없음

**Storage**: 파일(입력 `.md`, 출력 `exports/` 아래 SVG/PNG/PDF, 중간 산출물은 OS 임시 디렉토리)

**Testing**: 자동 테스트 스위트 없음(004와 동일). quickstart.md의 재현 샘플 + 저장소 `.zenuml/*.md` 회귀 비교(수정 전/후 SVG `cmp`)로 검증

**Target Platform**: Windows 11(주 사용 환경), 그 밖에 Node/Chromium이 도는 OS

**Project Type**: Claude Code Skill에 번들된 CLI 스크립트

**Performance Goals**: 다이어그램당 브라우저 페이지 1~2개 추가 수준(체감 수 초 이내). 브라우저 실행은 스크립트 1회당 1번으로 공유

**Constraints**: 잘리지 않던 다이어그램의 SVG는 바이트 단위 동일(FR-005). SVG를 DOM에서 재직렬화하지 않음(FR-006)

**Scale/Scope**: 스크립트 2개 수정(`export-diagrams.js`, `export-document-pdf.js`), 공용 모듈 1개 추가(`lib/fit-svg.js`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`는 아직 템플릿 placeholder 상태라 비준된 원칙이 없다 — 게이트 **N/A**, 위반 없음으로 진행한다(004와 동일한 처리).

**Post-Phase 1 재확인**: 설계 완료 후에도 constitution은 placeholder 상태 — 게이트 여전히 N/A.

## Project Structure

### Documentation (this feature)

```text
specs/005-fix-diagram-clipping/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── export-scripts.md
└── tasks.md             # /speckit-tasks 산출물
```

### Source Code (repository root)

```text
.claude/skills/exporting-markdown-diagrams/
├── SKILL.md                         # 변경 없음(사용법·출력 경로 규칙 불변, FR-010)
└── scripts/
    ├── export-diagrams.js           # 파이프라인 변경: mmdc→SVG → fit → svg 복사/png 캡처/pdf 인쇄
    ├── export-document-pdf.js       # Stage 1.5 추가: 추출 SVG fit 후 인라인
    └── lib/
        ├── fit-svg.js               # 신규: fitSvgFile / svgFileToPng / svgFileToPdf
        ├── run-mmdc.js              # 변경 없음
        ├── inline-svg.js            # 변경 없음
        └── export-dir.js            # 변경 없음
```

**Structure Decision**: 기존 스킬 디렉토리 구조를 그대로 쓰고, 두 스크립트가 공유하는 보정 로직만 `scripts/lib/`의 새 모듈로 둔다(기존 `lib/` 공용 모듈 관례와 동일).

## Complexity Tracking

해당 없음(constitution 게이트 없음, 새 의존성·새 프로젝트 없음).
