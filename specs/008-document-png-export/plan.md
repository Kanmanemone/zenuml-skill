# Implementation Plan: 문서 전체를 PNG 이미지로 내보내기

**Branch**: `008-document-png-export` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-document-png-export/spec.md`

## Summary

문서 전체 PNG는 기존 문서 PDF 파이프라인으로 같은 페이지 구성의 PDF를 임시로 만든 뒤, 그 PDF의 각 페이지를 PNG로 래스터화해 만든다. 이렇게 하면 모양(FR-003)과 페이지 나눔·장수(FR-002)가 PDF와 구조적으로 같아진다. 래스터화는 이미 쓰는 headless 브라우저 안에서 `pdfjs-dist`로 하고, 배율은 `png.scale`을 따른다. 문서 PDF 파이프라인은 공용 모듈로 빼서 PDF·PNG 두 스크립트가 함께 쓴다. SKILL.md의 형식·범위 규칙은 "문서 전체면 PDF 고정"에서 "문서 전체면 PDF·PNG 중 선택"으로 바꾼다.

## Technical Context

**Language/Version**: Node.js ESM(기존 스크립트와 동일, Node 24에서 확인)

**Primary Dependencies**: 기존 `@mermaid-js/mermaid-cli`, `markdown-it`, `puppeteer` + 신규 `pdfjs-dist`(PDF 페이지 래스터화, 순수 JS)

**Storage**: 파일(원본 옆 `output.directory`)

**Testing**: 자동화 프레임워크 없음. quickstart 시나리오를 실제 실행해 확인

**Target Platform**: Windows/macOS/Linux, headless Chromium(puppeteer 번들)

**Project Type**: Claude Code skill 번들 스크립트

**Performance Goals**: 기존 문서 PDF 변환 시간 + 페이지당 래스터화 시간. 별도 목표 없음

**Constraints**: 결정적 변환(004, FR-011). 실패 시 대체 형식으로 몰래 바꾸지 않음(FR-012). 문서 PDF와 다이어그램 변환의 기존 결과는 바뀌지 않음(SC-006).

**Scale/Scope**: 스크립트 1개 신규, 공용 모듈 1개 신규(기존 PDF 스크립트에서 추출), SKILL.md·설정 주석 갱신

## Constitution Check

`.specify/memory/constitution.md`가 템플릿 상태 — 게이트 **N/A**. Phase 1 후 재확인: 변화 없음.

## Project Structure

### Documentation (this feature)

```text
specs/008-document-png-export/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli.md
└── tasks.md
```

### Source Code (repository root)

```text
.claude/skills/exporting-markdown-diagrams/
├── SKILL.md                       # 문서 전체 형식 규칙(PDF·PNG), SVG 거절, 디스패치
├── settings.jsonc                 # defaults.pdfLayout·defaults.format 주석 갱신
├── settings.schema.json           # 같은 옵션의 description 갱신
└── scripts/
    ├── package.json               # pdfjs-dist 추가
    ├── export-document-pdf.js     # 공용 모듈을 쓰는 얇은 CLI로 정리(동작 동일)
    ├── export-document-png.js     # 신규 — 문서 전체 PNG
    └── lib/
        ├── document-pdf.js        # 신규 — 문서 → PDF 파이프라인(기존 코드 이동)
        └── rasterize-pdf.js       # 신규 — PDF 페이지 → PNG(pdfjs-dist, 브라우저 안)
```

**Structure Decision**: PNG를 PDF에서 파생시켜 두 형식이 같은 렌더링을 공유한다. 별도 HTML 스크린샷 경로를 만들면 인쇄 페이지 나눔을 재현할 수 없다(research.md).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 새 의존성 `pdfjs-dist` | 표준 인쇄 규격 PNG가 PDF와 같은 페이지 나눔을 가져야 함(FR-002) | HTML 전체 스크린샷을 고정 높이로 자르면 줄·표가 페이지 경계에서 잘리고 장수가 PDF와 달라짐 |
