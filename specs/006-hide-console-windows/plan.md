# Implementation Plan: 변환 중 터미널 창 깜빡임 제거

**Branch**: `006-hide-console-windows` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-hide-console-windows/spec.md`

## Summary

스킬이 띄우는 모든 headless 브라우저를 `chrome-headless-shell`(콘솔 서브시스템 → Windows에서 창 생성) 대신 같은 버전의 `chrome`(GUI 서브시스템, `headless: true`)으로 바꾸고, 산출물이 바뀌지 않도록 `--lang=en-US`를 함께 준다. 이 launch 설정을 `scripts/puppeteer-config.json` 한 파일에 두고, mmdc에는 `-p`로, 스크립트 자신의 `puppeteer.launch()`에는 같은 파일을 읽어 넘긴다.

## Technical Context

**Language/Version**: Node.js (ESM), v24.19.0

**Primary Dependencies**: `@mermaid-js/mermaid-cli` 11.16.0(`-p/--puppeteerConfigFile` 지원, 기본값 `{ headless: "shell" }`에 `Object.assign`으로 병합), `puppeteer` 25.8.0(설치 시 `chrome`과 `chrome-headless-shell` 둘 다 캐시에 받음) — 새 의존성 없음

**Storage**: 파일(설정 JSON 1개 추가)

**Testing**: 자동 테스트 없음. quickstart.md — 창 감시 스크립트로 새 창 수 측정 + SVG 바이트 비교

**Target Platform**: Windows 11(문제 발생 환경), 다른 OS도 같은 설정

**Project Type**: Claude Code Skill 번들 CLI 스크립트

**Performance Goals**: 변환 1회당 증가 1초 이내(SC-003)

**Constraints**: SVG 산출물 바이트 동일(FR-002), 설정은 한 곳(FR-003)

**Scale/Scope**: 설정 파일 1개 추가, `lib/run-mmdc.js`·`export-diagrams.js`·`export-document-pdf.js` 소폭 수정

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`가 템플릿 placeholder 상태 — 게이트 **N/A**, 위반 없음.

**Post-Phase 1 재확인**: 상태 변화 없음, 여전히 N/A.

## Project Structure

### Documentation (this feature)

```text
specs/006-hide-console-windows/
├── plan.md
├── research.md
├── quickstart.md
└── tasks.md             # /speckit-tasks 산출물
```

data-model.md와 contracts/는 만들지 않는다 — 다루는 데이터가 없고, 외부 인터페이스(CLI 인자·출력)가 바뀌지 않는다(FR-004).

### Source Code (repository root)

```text
.claude/skills/exporting-markdown-diagrams/scripts/
├── puppeteer-config.json        # 신규: { "headless": true, "args": ["--lang=en-US"] }
├── export-diagrams.js           # launch 옵션을 공통 설정으로
├── export-document-pdf.js       # launch 옵션을 공통 설정으로
└── lib/
    ├── browser-config.js        # 신규: 설정 파일 경로와 파싱된 launch 옵션 export
    └── run-mmdc.js              # mmdc 호출에 항상 `-p <puppeteer-config.json>` 추가
```

**Structure Decision**: 설정 값은 mmdc가 파일로만 받을 수 있으므로 JSON 파일을 단일 원천으로 두고, Node 쪽은 작은 `lib/browser-config.js`가 그 파일을 읽어 노출한다.

## Complexity Tracking

해당 없음.
