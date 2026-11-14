# Implementation Plan: 다이어그램 노드 hover로 책임·협력 보기

**Branch**: `009-hover-detail-panel` | **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-hover-detail-panel/spec.md`

## Summary

`generating-architecture-views`가 만든 구조 뷰 파일에서, Dependency 다이어그램의 각 노드에 마우스를 올리면 그 노드의 Responsibility와 그 노드가 의존하는 Collaboration이 패널로 뜨게 한다. 모델은 지금처럼 본문까지만 쓰고, 스킬에 새로 넣는 결정적 Python 스크립트 `scripts/apply_hover.py`가 저장된 파일을 읽어 (1) 노드마다 `click` 툴팁을 본문의 복사본으로 채우고, (2) 링크 없는 노드에 이동 없는 `click` 줄을 달고, (3) 파일 맨 아래에 `hover.position`별 고정 `<style>` 블록을 붙인다. 같은 스크립트를 다시 돌리면 본문 수정이 반영되고, hover를 끄면 기능 도입 전 형태로 되돌린다. 설정은 `settings.jsonc`의 `hover` 그룹(`enabled`, `responsibility`, `collaboration`, `position`)이며, 목록 값을 다루기 위해 설정 로더에 항목 목록 타입을 더한다.

## Technical Context

**Language/Version**: Python 3.9 이상에서 동작하는 스크립트(표준 라이브러리만, 3.10+ 전용 문법 `match`·런타임 `X | Y` 타입 표기 미사용) + Markdown 지침 문서(SKILL.md, references). 권장은 설치된 최신 안정판. 실행은 환경에 있는 인터프리터로 `python3 scripts/apply_hover.py ...`(없으면 `python`, `py -3` 순).

**Primary Dependencies**: 없음. Python 표준 라이브러리(`json`, `re`, `pathlib`, `argparse`, `sys`)만 쓴다. 주석 허용 JSON 파싱과 옵션 검증은 `exporting-markdown-diagrams/scripts/lib/settings.js`와 같은 동작을 이 스킬 안에 Python으로 옮겨 쓴다(스킬 독립성, 003 FR-014).

**Storage**: 파일 — 구조 뷰 파일 `.zenuml/<slug>.architecture.md`(제자리 덮어쓰기), 스킬 디렉터리의 `settings.jsonc`·`settings.schema.json`

**Testing**: 자동화 테스트 프레임워크 없음(기존 스킬과 동일). 고정 입력 파일(fixture)에 스크립트를 돌려 기대 출력과 바이트 비교하는 시나리오와 VS Code 미리보기 수동 확인을 [quickstart.md](quickstart.md)에 둔다.

**Target Platform**: Claude Code(Windows/macOS/Linux)에서 환경에 있는 Python으로 스크립트 실행(설치 단계 없음, Python이 없으면 hover만 건너뜀), 결과 확인은 VS Code 1.146 내장 Markdown 미리보기(Mermaid 12)

**Project Type**: Claude Code skill(지침 문서 + 번들 스크립트)

**Performance Goals**: 모델 출력 토큰 증가 0(SC-007) — 툴팁과 `<style>`은 스크립트가 만든다. 스크립트는 구조 뷰 파일 하나(수백 줄)를 1초 안에 처리한다.

**Constraints**: 결과는 결정적이고 멱등이어야 한다(FR-003). 본문은 바꾸지 않는다(FR-002). hover가 꺼지면 기능 도입 전 산출물과 같아야 한다(SC-005). 산출물에 더하는 표기는 최소(Assumptions) — 메타 주석이나 표식 주석을 넣지 않는다(003 AP-13c).

**Scale/Scope**: 새 Python 스크립트 1개(+ 보조 모듈 4개), 새 설정 옵션 4개(`hover.enabled`·`hover.responsibility`·`hover.collaboration`·`hover.position`), 설정 로더에 항목 목록 타입 1개, SKILL.md 규칙 개정(003 FR-016·017, 007 FR-018).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`가 템플릿 placeholder 상태 — 비준된 원칙이 없으므로 게이트 **N/A**, 위반 없음. Phase 1 설계 후 재확인: 변화 없음.

## Project Structure

### Documentation (this feature)

```text
specs/009-hover-detail-panel/
├── plan.md              # 이 파일
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── apply-hover-contract.md   # 스크립트 실행 규약과 구조 뷰 파일 변환 규칙
└── tasks.md             # /speckit-tasks 산출물
```

### Source Code (repository root)

```text
.claude/skills/generating-architecture-views/
├── SKILL.md                    # 개정 — 저장 후 apply-hover 실행 단계, AP-13c 허용 목록, click 툴팁 규칙, 링크 없는 노드 예외
├── settings.jsonc              # 개정 — hover 그룹(enabled·responsibility·collaboration·position)과 주석
├── settings.schema.json        # 개정 — 위 네 옵션, itemList 타입
├── references/
│   └── templates.md            # 개정 — 툴팁이 채워진 click 줄과 hoverOnly 줄 예시
└── scripts/                    # 신규
    ├── apply_hover.py          # 진입점: python scripts/apply_hover.py <file> [재정의 옵션]
    └── hover/                  # 패키지(__init__.py 포함)
        ├── settings.py         # exporting 스킬 로더와 같은 동작의 Python판 + itemList 타입
        ├── view_parser.py      # 구조 뷰 파일 → 노드·엣지·click 줄·본문 항목
        ├── panel_text.py       # 노드 패널 내용 조립(형식·이스케이프)
        └── style_blocks.py     # position별 고정 <style> 블록 두 벌

docs/hover-tooltip-test/        # 기존 테스트 키트(bottom: inline-style.md, node: node-25em.md) — CSS 원본

specs/009-hover-detail-panel/fixtures/   # 신규 — quickstart의 바이트 비교용 입력·기대 출력
```

**Structure Decision**: 스크립트는 이 스킬 디렉터리 안 `scripts/`에 둔다. 다른 스킬의 코드를 import하지 않는다(003 FR-014) — 설정 로더는 Python으로 옮겨 들고 온다. 언어는 외부 라이브러리가 필요 없는 텍스트 변환이라, Agent Skills 스크립트에서 가장 흔한 Python 표준 라이브러리로 쓴다(research R1). `<style>` 블록 원본은 VS Code에서 확인을 마친 테스트 키트의 CSS를 그대로 옮긴다.

## Complexity Tracking

위반 없음 — 비워 둔다.
